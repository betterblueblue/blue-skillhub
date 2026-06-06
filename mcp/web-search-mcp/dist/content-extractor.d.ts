import { ContentExtractionOptions, SearchResult } from './types.js';
export declare class ContentExtractor {
    private readonly defaultTimeout;
    private readonly maxContentLength;
    constructor();
    extractContent(options: ContentExtractionOptions): Promise<string>;
    extractContentForResults(results: SearchResult[], targetCount?: number): Promise<SearchResult[]>;
    private parseContent;
    private cleanTextContent;
    private getSpecificErrorMessage;
}
//# sourceMappingURL=content-extractor.d.ts.map