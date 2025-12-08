import { useMutation, useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { toast } from '@/components/ui/use-toast';

export function useHealthCheck() {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => apiClient.healthCheck(),
    refetchInterval: 30000, // Check every 30 seconds
  });
}

export function useGenerateText() {
  return useMutation({
    mutationFn: (data: {
      prompt: string;
      system_prompt?: string;
      max_tokens?: number;
      temperature?: number;
    }) => apiClient.generateText(data),
    onError: (error) => {
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to generate text',
        variant: 'destructive',
      });
    },
  });
}

export function useTextToSQL() {
  return useMutation({
    mutationFn: (data: {
      question: string;
      schema_context?: string;
    }) => apiClient.textToSQL(data),
    onError: (error) => {
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to convert to SQL',
        variant: 'destructive',
      });
    },
  });
}

export function useGenerateReport() {
  return useMutation({
    mutationFn: (data: {
      query_results: Record<string, any>;
      report_type?: string;
      additional_context?: string;
    }) => apiClient.generateReport(data),
    onError: (error) => {
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to generate report',
        variant: 'destructive',
      });
    },
  });
}
