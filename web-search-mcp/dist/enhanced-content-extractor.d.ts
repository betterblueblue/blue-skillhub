import { ContentExtractionOptions, SearchResult } from './types.js';
export declare class EnhancedContentExtractor {
    private readonly defaultTimeout;
    private readonly maxContentLength;
    private browserPool;
    private fallbackThreshold;
    constructor();
    extractContent(options: ContentExtractionOptions): Promise<string>;
    private extractWithAxios;
    private extractWithBrowser;
    private simulateHumanBehavior;
    private shouldUseBrowser;
    private isLowQualityContent;
    private getRandomHeaders;
    private getRandomUserAgent;
    private getRandomViewport;
    private getRandomTimezone;
    extractContentForResults(results: SearchResult[], targetCount?: number): Promise<SearchResult[]>;
    private parseContent;
    private cleanTextContent;
    private getSpecificErrorMessage;
    closeAll(): Promise<void>;
}
//# sourceMappingURL=enhanced-content-extractor.d.ts.map