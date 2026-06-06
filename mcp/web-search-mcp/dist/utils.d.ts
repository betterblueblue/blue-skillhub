/**
 * Utility functions for the web search MCP server
 */
export declare function cleanText(text: string, maxLength?: number): string;
export declare function getWordCount(text: string): number;
export declare function getContentPreview(text: string, maxLength?: number): string;
export declare function generateTimestamp(): string;
export declare function validateUrl(url: string): boolean;
export declare function sanitizeQuery(query: string): string;
export declare function getRandomUserAgent(): string;
export declare function delay(ms: number): Promise<void>;
export declare function isPdfUrl(url: string): boolean;
//# sourceMappingURL=utils.d.ts.map