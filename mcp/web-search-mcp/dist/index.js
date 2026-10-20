#!/usr/bin/env node
// Ensure critical env vars have defaults if not passed by MCP host
process.env.BROWSER_TYPES = process.env.BROWSER_TYPES || 'chromium';
process.env.BROWSER_HEADLESS = process.env.BROWSER_HEADLESS || 'true';
process.env.HTTP_PROXY = process.env.HTTP_PROXY || 'http://localhost:7890';
process.env.HTTPS_PROXY = process.env.HTTPS_PROXY || 'http://localhost:7890';
process.env.http_proxy = process.env.http_proxy || 'http://localhost:7890';
process.env.https_proxy = process.env.https_proxy || 'http://localhost:7890';
console.error('Web Search MCP Server starting...');
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { SearchEngine } from './search-engine.js';
import { EnhancedContentExtractor } from './enhanced-content-extractor.js';
import { isPdfUrl } from './utils.js';
class WebSearchMCPServer {
    server;
    searchEngine;
    contentExtractor;
    constructor() {
        this.server = new McpServer({
            name: 'web-search-mcp',
            version: '0.3.1',
        });
        this.searchEngine = new SearchEngine();
        this.contentExtractor = new EnhancedContentExtractor();
        this.setupTools();
        this.setupGracefulShutdown();
    }
    setupTools() {
        // Register the main web search tool (primary choice for comprehensive searches)
        this.server.tool('full-web-search', 'Search the web and fetch complete page content from top results. This is the most comprehensive web search tool. It searches the web and then follows the resulting links to extract their full page content, providing the most detailed and complete information available. Use get-web-search-summaries for a lightweight alternative.', {
            query: z.string().describe('Search query to execute (recommended for comprehensive research)'),
            limit: z.union([z.number(), z.string()]).transform((val) => {
                const num = typeof val === 'string' ? parseInt(val, 10) : val;
                if (isNaN(num) || num < 1 || num > 10) {
                    throw new Error('Invalid limit: must be a number between 1 and 10');
                }
                return num;
            }).default(5).describe('Number of results to return with full content (1-10)'),
            includeContent: z.union([z.boolean(), z.string()]).transform((val) => {
                if (typeof val === 'string') {
                    return val.toLowerCase() === 'true';
                }
                return Boolean(val);
            }).default(true).describe('Whether to fetch full page content (default: true)'),
            maxContentLength: z.union([z.number(), z.string()]).transform((val) => {
                const num = typeof val === 'string' ? parseInt(val, 10) : val;
                if (isNaN(num) || num < 0) {
                    throw new Error('Invalid maxContentLength: must be a non-negative number');
                }
                return num;
            }).optional().describe('Maximum characters per result content (0 = no limit). Usually not needed - content length is automatically optimized.'),
        }, async (args) => {
            console.error(`[MCP] Tool call received: full-web-search`);
            console.error(`[MCP] Raw arguments:`, JSON.stringify(args, null, 2));
            try {
                // Convert and validate arguments
                const validatedArgs = this.validateAndConvertArgs(args);
                // Auto-detect model types based on parameter formats
                // Llama models often send string parameters and struggle with large responses
                const isLikelyLlama = typeof args === 'object' && args !== null && (('limit' in args && typeof args.limit === 'string') ||
                    ('includeContent' in args && typeof args.includeContent === 'string'));
                // Detect models that handle large responses well (Qwen, Gemma, recent Deepseek)
                const isLikelyRobustModel = typeof args === 'object' && args !== null && (('limit' in args && typeof args.limit === 'number') &&
                    ('includeContent' in args && typeof args.includeContent === 'boolean'));
                // Only apply auto-limit if maxContentLength is not explicitly set (including 0)
                const hasExplicitMaxLength = typeof args === 'object' && args !== null && 'maxContentLength' in args;
                if (!hasExplicitMaxLength && isLikelyLlama) {
                    console.error(`[MCP] Detected potential Llama model (string parameters), applying content length limit`);
                    validatedArgs.maxContentLength = 2000; // Reasonable limit for Llama
                }
                // For robust models (Qwen, Gemma, recent Deepseek), remove maxContentLength if it's set to a low value
                if (isLikelyRobustModel && validatedArgs.maxContentLength && validatedArgs.maxContentLength < 5000) {
                    console.error(`[MCP] Detected robust model (numeric parameters), removing unnecessary content length limit`);
                    validatedArgs.maxContentLength = undefined;
                }
                console.error(`[MCP] Validated args:`, JSON.stringify(validatedArgs, null, 2));
                console.error(`[MCP] Starting web search...`);
                const result = await this.handleWebSearch(validatedArgs);
                console.error(`[MCP] Search completed, found ${result.results.length} results`);
                // Format the results as a comprehensive text response
                let responseText = `Search completed for "${result.query}" with ${result.total_results} results:\n\n`;
                // Add status line if available
                if (result.status) {
                    responseText += `**Status:** ${result.status}\n\n`;
                }
                const maxLength = validatedArgs.maxContentLength;
                result.results.forEach((searchResult, idx) => {
                    responseText += `**${idx + 1}. ${searchResult.title}**\n`;
                    responseText += `URL: ${searchResult.url}\n`;
                    responseText += `Description: ${searchResult.description}\n`;
                    if (searchResult.fullContent && searchResult.fullContent.trim()) {
                        let content = searchResult.fullContent;
                        if (maxLength && maxLength > 0 && content.length > maxLength) {
                            content = content.substring(0, maxLength) + `\n\n[Content truncated at ${maxLength} characters]`;
                        }
                        responseText += `\n**Full Content:**\n${content}\n`;
                    }
                    else if (searchResult.contentPreview && searchResult.contentPreview.trim()) {
                        let content = searchResult.contentPreview;
                        if (maxLength && maxLength > 0 && content.length > maxLength) {
                            content = content.substring(0, maxLength) + `\n\n[Content truncated at ${maxLength} characters]`;
                        }
                        responseText += `\n**Content Preview:**\n${content}\n`;
                    }
                    else if (searchResult.fetchStatus === 'error') {
                        responseText += `\n**Content Extraction Failed:** ${searchResult.error}\n`;
                    }
                    responseText += `\n---\n\n`;
                });
                responseText += this.formatEngineHealth(result);
                return {
                    content: [
                        {
                            type: 'text',
                            text: responseText,
                        },
                    ],
                };
            }
            catch (error) {
                console.error(`[MCP] Error in tool handler:`, error);
                throw error;
            }
        });
        // Register the lightweight web search summaries tool (secondary choice for quick results)
        this.server.tool('get-web-search-summaries', 'Search the web and return only the search result snippets/descriptions without following links to extract full page content. This is a lightweight alternative to full-web-search for when you only need brief search results. For comprehensive information, use full-web-search instead.', {
            query: z.string().describe('Search query to execute (lightweight alternative)'),
            limit: z.union([z.number(), z.string()]).transform((val) => {
                const num = typeof val === 'string' ? parseInt(val, 10) : val;
                if (isNaN(num) || num < 1 || num > 10) {
                    throw new Error('Invalid limit: must be a number between 1 and 10');
                }
                return num;
            }).default(5).describe('Number of search results to return (1-10)'),
        }, async (args) => {
            console.error(`[MCP] Tool call received: get-web-search-summaries`);
            console.error(`[MCP] Raw arguments:`, JSON.stringify(args, null, 2));
            try {
                // Validate arguments
                if (typeof args !== 'object' || args === null) {
                    throw new Error('Invalid arguments: args must be an object');
                }
                const obj = args;
                if (!obj.query || typeof obj.query !== 'string') {
                    throw new Error('Invalid arguments: query is required and must be a string');
                }
                let limit = 5; // default
                if (obj.limit !== undefined) {
                    const limitValue = typeof obj.limit === 'string' ? parseInt(obj.limit, 10) : obj.limit;
                    if (typeof limitValue !== 'number' || isNaN(limitValue) || limitValue < 1 || limitValue > 10) {
                        throw new Error('Invalid limit: must be a number between 1 and 10');
                    }
                    limit = limitValue;
                }
                console.error(`[MCP] Starting web search summaries...`);
                try {
                    // Use existing search engine to get results with snippets
                    const searchResponse = await this.searchEngine.search({
                        query: obj.query,
                        numResults: limit,
                    });
                    // const searchTime = Date.now() - startTime; // Unused for now
                    // Convert to summary format (no content extraction)
                    const summaryResults = searchResponse.results.map(item => ({
                        title: item.title,
                        url: item.url,
                        description: item.description,
                        timestamp: item.timestamp,
                    }));
                    console.error(`[MCP] Search summaries completed, found ${summaryResults.length} results`);
                    // Format the results as text
                    let responseText = `Search summaries for "${obj.query}" with ${summaryResults.length} results:\n\n`;
                    summaryResults.forEach((summary, i) => {
                        responseText += `**${i + 1}. ${summary.title}**\n`;
                        responseText += `URL: ${summary.url}\n`;
                        responseText += `Description: ${summary.description}\n`;
                        responseText += `\n---\n\n`;
                    });
                    responseText += this.formatEngineHealth(searchResponse);
                    return {
                        content: [
                            {
                                type: 'text',
                                text: responseText,
                            },
                        ],
                    };
                }
                finally {
                    // Ensure browsers are cleaned up after search-only operations
                    // This prevents EventEmitter memory leaks when browsers accumulate listeners
                    try {
                        await this.searchEngine.closeAll();
                    }
                    catch (cleanupError) {
                        console.error(`[MCP] Error during browser cleanup:`, cleanupError);
                    }
                }
            }
            catch (error) {
                console.error(`[MCP] Error in get-web-search-summaries tool handler:`, error);
                throw error;
            }
        });
        // Register the single page content extraction tool
        this.server.tool('get-single-web-page-content', 'Extract and return the full content from a single web page URL. This tool follows a provided URL and extracts the main page content. Useful for getting detailed content from a specific webpage without performing a search.', {
            url: z.string().url().describe('The URL of the web page to extract content from'),
            maxContentLength: z.union([z.number(), z.string()]).transform((val) => {
                const num = typeof val === 'string' ? parseInt(val, 10) : val;
                if (isNaN(num) || num < 0) {
                    throw new Error('Invalid maxContentLength: must be a non-negative number');
                }
                return num;
            }).optional().describe('Maximum characters for the extracted content (0 = no limit, undefined = use default limit). Usually not needed - content length is automatically optimized.'),
        }, async (args) => {
            console.error(`[MCP] Tool call received: get-single-web-page-content`);
            console.error(`[MCP] Raw arguments:`, JSON.stringify(args, null, 2));
            try {
                // Validate arguments
                if (typeof args !== 'object' || args === null) {
                    throw new Error('Invalid arguments: args must be an object');
                }
                const obj = args;
                if (!obj.url || typeof obj.url !== 'string') {
                    throw new Error('Invalid arguments: url is required and must be a string');
                }
                let maxContentLength;
                if (obj.maxContentLength !== undefined) {
                    const maxLengthValue = typeof obj.maxContentLength === 'string' ? parseInt(obj.maxContentLength, 10) : obj.maxContentLength;
                    if (typeof maxLengthValue !== 'number' || isNaN(maxLengthValue) || maxLengthValue < 0) {
                        throw new Error('Invalid maxContentLength: must be a non-negative number');
                    }
                    // If maxContentLength is 0, treat it as "no limit" (undefined)
                    maxContentLength = maxLengthValue === 0 ? undefined : maxLengthValue;
                }
                console.error(`[MCP] Starting single page content extraction for: ${obj.url}`);
                // Use existing content extractor to get page content
                const content = await this.contentExtractor.extractContent({
                    url: obj.url,
                    maxContentLength,
                });
                // Get page title from URL (simple extraction)
                const urlObj = new URL(obj.url);
                const title = urlObj.hostname + urlObj.pathname;
                // Create content preview and word count
                // const contentPreview = content.length > 200 ? content.substring(0, 200) + '...' : content; // Unused for now
                const wordCount = content.split(/\s+/).filter(word => word.length > 0).length;
                console.error(`[MCP] Single page content extraction completed, extracted ${content.length} characters`);
                // Format the result as text
                let responseText = `**Page Content from: ${obj.url}**\n\n`;
                responseText += `**Title:** ${title}\n`;
                responseText += `**Word Count:** ${wordCount}\n`;
                responseText += `**Content Length:** ${content.length} characters\n\n`;
                if (maxContentLength && maxContentLength > 0 && content.length > maxContentLength) {
                    responseText += `**Content (truncated at ${maxContentLength} characters):**\n${content.substring(0, maxContentLength)}\n\n[Content truncated at ${maxContentLength} characters]`;
                }
                else {
                    responseText += `**Content:**\n${content}`;
                }
                return {
                    content: [
                        {
                            type: 'text',
                            text: responseText,
                        },
                    ],
                };
            }
            catch (error) {
                console.error(`[MCP] Error in get-single-web-page-content tool handler:`, error);
                throw error;
            }
        });
        // Engine self-test. Exposed as a tool (not just the health-check.mjs CLI)
        // so the agent can decide to run it on its own.
        this.server.tool('check-search-health', [
            'Diagnose the web search engines themselves. Each engine (Google, DuckDuckGo, Bing, Brave) is probed separately with a fixed test query, and every engine is reported as working, throttled/blocked (external, transient), or parser-broken (the site changed its HTML and the parser needs a code fix).',
            '',
            'Call this tool when:',
            '- a search returned 0 results, or results that look unrelated to the query;',
            '- a previous search response included a "[引擎状态]" / engine-status section with a warning, or showed a fallback engine like "Axios DuckDuckGo" / "Browser Bing" instead of Google;',
            '- the user reports that search is broken, slow, or returning junk;',
            '- you are about to rely on many searches and want to know whether the tool is healthy first.',
            '',
            'This is diagnostic only: it does not search for anything the user asked about, so do not call it to answer a question. It takes ~5-15 seconds because it launches a real browser per engine.',
        ].join('\n'), {
            // No required arguments: the point is that the agent can call it on its own.
            engine: z.string().optional().describe('Optional: only test one engine. One of "google", "ddg", "bing", "brave". Omit to test all.'),
        }, async (args) => {
            console.error(`[MCP] Tool call received: check-search-health`);
            try {
                const report = await this.runEngineHealthCheck(args?.engine);
                return {
                    content: [
                        {
                            type: 'text',
                            text: report,
                        },
                    ],
                };
            }
            catch (error) {
                console.error(`[MCP] Error in check-search-health tool handler:`, error);
                throw error;
            }
        });
    }
    // Runs the same per-engine probe that health-check.mjs does, but returns text
    // the agent can read. Never throws for a broken engine: a broken engine is a
    // successful diagnosis, not a tool failure.
    async runEngineHealthCheck(engineFilter) {
        const PROBE_QUERY = process.env.HEALTH_CHECK_QUERY || 'bimetallic thermometer calibration';
        const ENGINES = [
            { key: 'google', name: 'Browser Google', method: 'tryBrowserGoogleSearch' },
            { key: 'ddg', name: 'Axios DuckDuckGo', method: 'tryDuckDuckGoSearch' },
            { key: 'bing', name: 'Browser Bing', method: 'tryBrowserBingSearch' },
            { key: 'brave', name: 'Browser Brave', method: 'tryBrowserBraveSearch' },
        ];
        const filter = typeof engineFilter === 'string' ? engineFilter.toLowerCase() : null;
        const targets = filter ? ENGINES.filter(e => e.key === filter) : ENGINES;
        if (targets.length === 0) {
            return `Unknown engine "${engineFilter}". Valid values: google, ddg, bing, brave.`;
        }
        const rows = [];
        for (const spec of targets) {
            const startedAt = Date.now();
            let status = 'ok';
            let detail = '';
            let count = 0;
            // Probe twice before declaring a parser broken: one miss can just be
            // throttling, and telling the agent to fix code over a hiccup is worse
            // than saying nothing.
            for (let attempt = 0; attempt < 2; attempt++) {
                this.searchEngine.lastEngineBlocked = false;
                try {
                    const found = await this.searchEngine[spec.method](PROBE_QUERY, 3, 15000);
                    count = found.length;
                    if (count > 0) {
                        status = 'ok';
                        detail = `${count} results`;
                        break;
                    }
                    if (this.searchEngine.lastEngineBlocked) {
                        status = 'blocked';
                        detail = 'throttled or bot-checked';
                        break;
                    }
                    status = 'broken';
                    detail = 'served a page but 0 results were parsed';
                }
                catch (error) {
                    const message = error instanceof Error ? error.message : String(error);
                    status = this.searchEngine.lastEngineBlocked || /bot-check|captcha|rate limit/i.test(message)
                        ? 'blocked'
                        : 'error';
                    detail = message.slice(0, 160);
                    if (status === 'blocked')
                        break;
                }
            }
            rows.push({ name: spec.name, status, detail, count, ms: Date.now() - startedAt });
            this.searchEngine.lastEngineBlocked = false;
        }
        const broken = rows.filter(r => r.status === 'broken' || r.status === 'error');
        const blocked = rows.filter(r => r.status === 'blocked');
        const healthy = rows.filter(r => r.status === 'ok');
        const lines = [];
        lines.push(`Web search engine health check (probe query: "${PROBE_QUERY}")`);
        lines.push('');
        const label = { ok: 'OK', blocked: 'BLOCKED (external)', broken: 'PARSER BROKEN', error: 'ERROR' };
        for (const r of rows) {
            lines.push(`- ${r.name}: ${label[r.status] || r.status} - ${r.detail} (${r.ms}ms)`);
        }
        lines.push('');
        if (broken.length > 0) {
            lines.push(`VERDICT: ${broken.map(r => r.name).join(', ')} is/are broken.`);
            lines.push('This is a code problem, not a transient one: the search engine changed its HTML and the parser in dist/search-engine.js no longer matches it. The parse*Results functions need updating.');
            lines.push('Search still works through the remaining engines, but results may be slower or lower quality. Tell the user what broke.');
        }
        else if (blocked.length === rows.length) {
            lines.push('VERDICT: every engine is throttled or blocked.');
            lines.push('This is external (rate limiting or bot detection from the provider or the proxy exit IP), not a code bug. Waiting usually fixes it. If it persists, the proxy exit IP may be burned.');
        }
        else {
            lines.push(`VERDICT: healthy. Working engines: ${healthy.map(r => r.name).join(', ') || 'none'}.`);
            if (blocked.length > 0) {
                lines.push(`Blocked but not a code problem (fallback engines): ${blocked.map(r => r.name).join(', ')}.`);
            }
            if (healthy.length === 0) {
                lines.push('No engine produced results; search is currently unusable.');
            }
        }
        return lines.join('\n');
    }
    validateAndConvertArgs(args) {
        if (typeof args !== 'object' || args === null) {
            throw new Error('Invalid arguments: args must be an object');
        }
        const obj = args;
        // Ensure query is a string
        if (!obj.query || typeof obj.query !== 'string') {
            throw new Error('Invalid arguments: query is required and must be a string');
        }
        // Convert limit to number if it's a string
        let limit = 5; // default
        if (obj.limit !== undefined) {
            const limitValue = typeof obj.limit === 'string' ? parseInt(obj.limit, 10) : obj.limit;
            if (typeof limitValue !== 'number' || isNaN(limitValue) || limitValue < 1 || limitValue > 10) {
                throw new Error('Invalid limit: must be a number between 1 and 10');
            }
            limit = limitValue;
        }
        // Convert includeContent to boolean if it's a string
        let includeContent = true; // default
        if (obj.includeContent !== undefined) {
            if (typeof obj.includeContent === 'string') {
                includeContent = obj.includeContent.toLowerCase() === 'true';
            }
            else {
                includeContent = Boolean(obj.includeContent);
            }
        }
        return {
            query: obj.query,
            limit,
            includeContent,
        };
    }
    async handleWebSearch(input) {
        const startTime = Date.now();
        const { query, limit = 5, includeContent = true } = input;
        console.error(`[web-search-mcp] DEBUG: handleWebSearch called with limit=${limit}, includeContent=${includeContent}`);
        try {
            // Request extra search results to account for potential PDF files that will be skipped
            // Request up to 2x the limit or at least 5 extra results, capped at 10 (Google's max)
            const searchLimit = includeContent ? Math.min(limit * 2 + 2, 10) : limit;
            console.error(`[web-search-mcp] DEBUG: Requesting ${searchLimit} search results to get ${limit} non-PDF content results`);
            // Perform the search
            const searchResponse = await this.searchEngine.search({
                query,
                numResults: searchLimit,
            });
            const searchResults = searchResponse.results;
            // Log search summary
            const pdfCount = searchResults.filter(result => isPdfUrl(result.url)).length;
            const followedCount = searchResults.length - pdfCount;
            console.error(`[web-search-mcp] DEBUG: Search engine: ${searchResponse.engine}; ${limit} requested/${searchResults.length} obtained; PDF: ${pdfCount}; ${followedCount} followed.`);
            // Extract content from each result if requested, with target count
            const enhancedResults = includeContent
                ? await this.contentExtractor.extractContentForResults(searchResults, limit)
                : searchResults.slice(0, limit); // If not extracting content, just take the first 'limit' results
            // Log extraction summary with failure reasons and generate combined status
            let combinedStatus = `Search engine: ${searchResponse.engine}; ${limit} result requested/${searchResults.length} obtained; PDF: ${pdfCount}; ${followedCount} followed`;
            if (includeContent) {
                const successCount = enhancedResults.filter(r => r.fetchStatus === 'success').length;
                const failedResults = enhancedResults.filter(r => r.fetchStatus === 'error');
                const failedCount = failedResults.length;
                const failureReasons = this.categorizeFailureReasons(failedResults);
                const failureReasonText = failureReasons.length > 0 ? ` (${failureReasons.join(', ')})` : '';
                console.error(`[web-search-mcp] DEBUG: Links requested: ${limit}; Successfully extracted: ${successCount}; Failed: ${failedCount}${failureReasonText}; Results: ${enhancedResults.length}.`);
                // Add extraction info to combined status
                combinedStatus += `; Successfully extracted: ${successCount}; Failed: ${failedCount}; Results: ${enhancedResults.length}`;
            }
            const searchTime = Date.now() - startTime;
            return {
                results: enhancedResults,
                total_results: enhancedResults.length,
                search_time_ms: searchTime,
                query,
                status: combinedStatus,
                diagnostics: searchResponse?.diagnostics || [],
                warnings: searchResponse?.warnings || [],
            };
        }
        catch (error) {
            console.error('Web search error:', error);
            throw new Error(`Web search failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
    }
    // Appends engine health to the tool response text. Anything that goes only to
    // stderr is invisible to the agent, so degradation has to be written here.
    formatEngineHealth(searchResponse) {
        const diagnostics = searchResponse?.diagnostics || [];
        const warnings = searchResponse?.warnings || [];
        if (diagnostics.length === 0)
            return '';
        const lines = ['', '---', '[引擎状态]'];
        for (const d of diagnostics) {
            const label = {
                ok: '正常',
                'off-topic': '结果无关',
                blocked: '被反爬拦截',
                'no-results': '页面解析不出结果',
                error: '报错',
                skipped: '未尝试',
            }[d.outcome] || d.outcome;
            lines.push(`- ${d.engine}: ${label}（${d.detail}，${d.ms}ms）`);
        }
        if (warnings.length > 0) {
            lines.push('');
            lines.push('⚠️ 需要关注：');
            for (const w of warnings)
                lines.push(`- ${w}`);
        }
        // Point at the self-test when anything looks off, otherwise the agent has no
        // reason to discover that the tool exists.
        const problematic = diagnostics.filter(d =>
            d.outcome === 'no-results' || d.outcome === 'error' || d.outcome === 'off-topic');
        const degradedOnly = diagnostics.length > 0 && diagnostics[0].outcome !== 'ok';
        if (problematic.length > 0 || degradedOnly || warnings.length > 0) {
            lines.push('');
            lines.push('排查建议：可以调用 check-search-health 工具逐台检查搜索引擎，它会区分"解析器失效（需要改代码）"和"临时限流（等一会儿就好）"。');
        }
        return lines.join('\n') + '\n';
    }
    categorizeFailureReasons(failedResults) {
        const reasonCounts = new Map();
        failedResults.forEach(result => {
            if (result.error) {
                const category = this.categorizeError(result.error);
                reasonCounts.set(category, (reasonCounts.get(category) || 0) + 1);
            }
        });
        return Array.from(reasonCounts.entries()).map(([reason, count]) => count > 1 ? `${reason} (${count})` : reason);
    }
    categorizeError(errorMessage) {
        const lowerError = errorMessage.toLowerCase();
        if (lowerError.includes('timeout') || lowerError.includes('timed out')) {
            return 'Timeout';
        }
        if (lowerError.includes('403') || lowerError.includes('forbidden')) {
            return 'Access denied';
        }
        if (lowerError.includes('404') || lowerError.includes('not found')) {
            return 'Not found';
        }
        if (lowerError.includes('bot') || lowerError.includes('captcha') || lowerError.includes('unusual traffic')) {
            return 'Bot detection';
        }
        if (lowerError.includes('too large') || lowerError.includes('content length') || lowerError.includes('maxcontentlength')) {
            return 'Content too long';
        }
        if (lowerError.includes('ssl') || lowerError.includes('certificate') || lowerError.includes('tls')) {
            return 'SSL error';
        }
        if (lowerError.includes('network') || lowerError.includes('connection') || lowerError.includes('econnrefused')) {
            return 'Network error';
        }
        if (lowerError.includes('dns') || lowerError.includes('hostname')) {
            return 'DNS error';
        }
        return 'Other error';
    }
    setupGracefulShutdown() {
        // Handle unhandled promise rejections
        process.on('unhandledRejection', (reason, promise) => {
            console.error('Unhandled Rejection at:', promise, 'reason:', reason);
            // Don't exit on unhandled rejections, just log them
        });
        // Handle uncaught exceptions
        process.on('uncaughtException', (error) => {
            console.error('Uncaught Exception:', error);
            // Don't exit on uncaught exceptions in MCP context
        });
        // Graceful shutdown - close browsers when process exits
        process.on('SIGINT', async () => {
            console.error('Shutting down gracefully...');
            try {
                await Promise.all([
                    this.contentExtractor.closeAll(),
                    this.searchEngine.closeAll()
                ]);
            }
            catch (error) {
                console.error('Error during graceful shutdown:', error);
            }
            process.exit(0);
        });
        process.on('SIGTERM', async () => {
            console.error('Shutting down gracefully...');
            try {
                await Promise.all([
                    this.contentExtractor.closeAll(),
                    this.searchEngine.closeAll()
                ]);
            }
            catch (error) {
                console.error('Error during graceful shutdown:', error);
            }
            process.exit(0);
        });
    }
    async run() {
        console.error('Setting up MCP server...');
        const transport = new StdioServerTransport();
        console.error('Connecting to transport...');
        await this.server.connect(transport);
        console.error('Web Search MCP Server started');
        console.error('Server timestamp:', new Date().toISOString());
        console.error('Waiting for MCP messages...');
    }
}
// Start the server
const server = new WebSearchMCPServer();
server.run().catch((error) => {
    if (error instanceof Error) {
        console.error('Server error:', error.message);
    }
    else {
        console.error('Server error:', error);
    }
    process.exit(1);
});
//# sourceMappingURL=index.js.map