export interface SearchResult {
    title: string;
    url: string;
    description: string;
    fullContent: string;
    contentPreview: string;
    wordCount: number;
    timestamp: string;
    fetchStatus: 'success' | 'error' | 'timeout';
    error?: string;
}
export interface SearchResponse {
    query: string;
    limit: number;
    results: SearchResult[];
    totalFound: number;
    searchTimestamp: string;
    processingTimeMs: number;
}
export interface SearchOptions {
    query: string;
    numResults?: number;
    timeout?: number;
}
export interface ContentExtractionOptions {
    url: string;
    timeout?: number;
    maxContentLength?: number;
}
export interface WebSearchToolInput {
    query: string;
    limit?: number;
    includeContent?: boolean;
    maxContentLength?: number;
}
export interface WebSearchToolOutput {
    results: SearchResult[];
    total_results: number;
    search_time_ms: number;
    query: string;
    status?: string;
}
export interface SearchSummaryResult {
    title: string;
    url: string;
    description: string;
    timestamp: string;
}
export interface SearchSummaryOutput {
    results: SearchSummaryResult[];
    total_results: number;
    search_time_ms: number;
    query: string;
}
export interface SinglePageContentOutput {
    url: string;
    title: string;
    content: string;
    contentPreview: string;
    wordCount: number;
    timestamp: string;
    fetchStatus: 'success' | 'error';
    error?: string;
}
export interface SearchResultWithMetadata {
    results: SearchResult[];
    engine: string;
}
//# sourceMappingURL=types.d.ts.map