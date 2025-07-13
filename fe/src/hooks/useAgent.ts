import { useRef, useEffect } from 'react';
import { useXAgent, useXChat } from '@ant-design/x';
import { getEventType, type AgentEvent, type BubbleDataType, type MessageEvent} from '../types';
import { useChatStore } from '../store';
import { combineEvents, formatToHTML, formatMessageEvent } from '../utils/agentEventFormatter';

export const useAgent = () => {
  const abortController = useRef<AbortController | null>(null);
  // Use Zustand's selector pattern to properly subscribe to state changes
  const agentEvents = useChatStore(state => state.agentEvents);
  const isProcessing = useChatStore(state => state.isProcessing);
  const setAgentEvents = useChatStore(state => state.setAgentEvents);
  const setIsProcessing = useChatStore(state => state.setIsProcessing);

  // Custom request function for the agent
  const customRequest = async (
    info: { message: {content: string} },
    callbacks: {
      onUpdate: (chunk: string) => void;
      onSuccess: (chunks: string[]) => void;
      onError: (error: Error) => void;
      onStream?: (abortController: AbortController) => void;
    }
  ) => {
    // Get the latest selectedAgent value directly from the store
    const currentSelectedAgent = useChatStore.getState().selectedAgent;
    
    if (!currentSelectedAgent) {
      callbacks.onError(new Error('No agent selected'));
      return;
    }

    setIsProcessing(true);
    setAgentEvents([]);
    
    try {
      // Create a new AbortController for this request
      const controller = new AbortController();
      if (callbacks.onStream) {
        callbacks.onStream(controller);
      }
      
      // Call the stream_chat API with the correct parameters
      console.log('Sending request with agent ID:', currentSelectedAgent.id);
      console.log('User message:', info.message);
      
      const response = await fetch('/api/agent/stream_chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
        },
        body: JSON.stringify({
          agent_id: currentSelectedAgent.id,
          user_message: info.message.content
        })
      });
      
      console.log('Response status:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      // Get the reader from the response body
      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('Response body is null');
      }
      
      // Process the stream
      const decoder = new TextDecoder();
      let accumulatedEvents: AgentEvent[] = [];
      const isStreamingEnabled = useChatStore.getState().streamingEnabled;
      
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          break;
        }
        
        // Decode the chunk
        const chunk = decoder.decode(value);
        
        // Process the SSE data
        const lines = chunk.split('\n\n');
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const eventData = JSON.parse(line.substring(6));

              if( getEventType(eventData) === "message" ) {
                accumulatedEvents = [...accumulatedEvents, eventData];
                setAgentEvents(accumulatedEvents);
              }
              
              let formattedContent = '';
              let htmlContent = '';
              
              // Format the events based on streaming mode
              if (isStreamingEnabled) {
                
                formattedContent = combineEvents(accumulatedEvents);
                htmlContent = formatToHTML(formattedContent);
              } else {
                
                // Filter to only include message events
                const currentMessageEvents = accumulatedEvents as MessageEvent[];
                
                if (currentMessageEvents.length > 0) {
                  for (const msgEvent of currentMessageEvents) {
                    const formatted = formatMessageEvent(msgEvent);
                    htmlContent += formatToHTML(formatted);
                  }
                  
                } else {
                  // If no message events yet, show a loading message
                  htmlContent = formatToHTML("Processing...");
                }
              }
              
              // Update the UI with the formatted HTML content
              callbacks.onUpdate(htmlContent);
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }
      
      // Complete the request
      let finalContent = '';
      let htmlContent = '';
      
      // Format the final content based on streaming mode
      if (isStreamingEnabled) {
        // In streaming mode, show all events
        finalContent = combineEvents(accumulatedEvents);
        htmlContent = formatToHTML(finalContent);
      } else {
        // In non-streaming mode, only show message events
        const finalMessageEvents = accumulatedEvents.filter(event => getEventType(event) === 'message') as MessageEvent[];
        if (finalMessageEvents.length > 0) {

          for (const msgEvent of finalMessageEvents) {
            const formatted = formatMessageEvent(msgEvent);
            htmlContent += formatToHTML(formatted);
          }
        } else {
          // If no message events, show all events as fallback
          finalContent = combineEvents(accumulatedEvents);
          htmlContent = formatToHTML(finalContent);
        }
      }
      
      callbacks.onSuccess([htmlContent]);
    } catch (error) {
      console.error('Error in stream chat:', error);
      callbacks.onError(error instanceof Error ? error : new Error(String(error)));
    } finally {
      setIsProcessing(false);
    }
  };

  // Create the agent with our custom request function
  const [agent] = useXAgent<BubbleDataType, { message: {content: string}}, string>({
    request: customRequest,
  });
  
  const loading = agent.isRequesting() || isProcessing;

  // Use the XChat hook with our agent
  const { onRequest, messages: agentMessages } = useXChat({
    agent,
    requestFallback: (_, { error }) => {
      if (error.name === 'AbortError') {
        return {
          content: 'Request is aborted',
          role: 'assistant',
        };
      }
      console.error('Request failed:', error);
      return {
        content: 'Request failed, please try again!',
        role: 'assistant',
      };
    },
    transformMessage: (info) => {
      const { originMessage, chunk } = info || {};
      
      // If we have a chunk, use it directly
      if (chunk) {
        return {
          content: chunk,
          role: 'assistant',
        };
      }
      
      // Otherwise, return the original message or an empty one
      return {
        content: originMessage?.content || '',
        role: 'assistant',
      };
    },
    resolveAbortController: (controller) => {
      abortController.current = controller;
    },
  });

  // Get setMessages from store using selector pattern
  const setMessages = useChatStore(state => state.setMessages);
  
  // Sync agent messages with store
  useEffect(() => {
    if (agentMessages && agentMessages.length > 0) {
      // Convert agent messages to the format expected by the store
      const convertedMessages = agentMessages.map(item => ({
        message: item.message,
        status: item.status === 'loading' ? 'loading' as const : 
                item.status === 'error' ? 'error' as const : 'done' as const
      }));
      setMessages(convertedMessages);
    }
  }, [agentMessages, setMessages]);


  // Use useEffect to create a memoized handleSubmit function that updates when selectedAgent changes
  const handleSubmit = (val: string) => {
    if (!val) return;

    if (loading) {
      console.error('Request is in progress, please wait for the request to complete.');
      return;
    }

    // Get the latest selectedAgent value directly from the store
    const currentSelectedAgent = useChatStore.getState().selectedAgent;
    
    if (!currentSelectedAgent) {
      console.error('Please select an agent first');
      return;
    }

    console.log('Submitting with agent:', currentSelectedAgent.display_name);
    
    onRequest({
      stream: true,
      message: {role: 'user', content: val}
    });
  };

  const handleAbort = () => {
    abortController.current?.abort();
  };

  return {
    agent,
    loading,
    handleSubmit,
    handleAbort,
    agentEvents,
  };
};
