/**
 * Utility functions for the web search MCP server
 */

/**
 * Smart truncation that preserves sentence boundaries.
 * Instead of hard-cutting at maxLength (which can break mid-sentence or mid-word),
 * this finds the last complete sentence before the limit.
 */
export function smartTruncate(text, maxLength) {
    if (!text || text.length <= maxLength) return text;

    // First pass: try to cut at a sentence boundary (。！？.!? followed by space or end)
    const truncated = text.substring(0, maxLength);
    // Match sentence-ending punctuation: Chinese (。！？) and English (.!?) followed by space/newline or end
    const sentenceEndRegex = /[。！？.!?][\s\n]/g;
    let lastSentenceEnd = -1;
    let match;
    while ((match = sentenceEndRegex.exec(truncated)) !== null) {
        lastSentenceEnd = match.index + match[0].length;
    }

    if (lastSentenceEnd > maxLength * 0.6) {
        // Found a good sentence boundary in the latter 40% of the text — use it
        return text.substring(0, lastSentenceEnd).trim();
    }

    // Second pass: try paragraph break (\n\n or \n)
    const lastNewline = truncated.lastIndexOf('\n', maxLength);
    if (lastNewline > maxLength * 0.6) {
        return text.substring(0, lastNewline).trim();
    }

    // Third pass: try last space (don't break mid-word)
    const lastSpace = truncated.lastIndexOf(' ', maxLength - 1);
    if (lastSpace > maxLength * 0.6) {
        return text.substring(0, lastSpace).trim();
    }

    // Fallback: hard cut (better than nothing, but add ellipsis indicator)
    return truncated.trim();
}

export function cleanText(text, maxLength = 6000) {
    const cleaned = text
        .replace(/[ \t]+/g, ' ') // Collapse horizontal whitespace only (preserve \n for paragraph structure)
        .replace(/\n{3,}/g, '\n\n') // Collapse 3+ newlines to 2 (keep paragraph breaks)
        .trim();
    return smartTruncate(cleaned, maxLength);
}
export function getWordCount(text) {
    return text.trim().split(/\s+/).filter(word => word.length > 0).length;
}
export function getContentPreview(text, maxLength = 500) {
    const cleaned = cleanText(text, maxLength);
    return cleaned.length === maxLength ? cleaned + '...' : cleaned;
}
export function generateTimestamp() {
    return new Date().toISOString();
}
export function validateUrl(url) {
    try {
        const parsed = new URL(url);
        return parsed.protocol === 'http:' || parsed.protocol === 'https:';
    }
    catch {
        return false;
    }
}
export function sanitizeQuery(query) {
    return query.trim().substring(0, 1000); // Limit query length
}
export function getRandomUserAgent() {
    const userAgents = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    ];
    return userAgents[Math.floor(Math.random() * userAgents.length)];
}
export function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
export function isPdfUrl(url) {
    try {
        const parsed = new URL(url);
        return parsed.pathname.toLowerCase().endsWith('.pdf');
    }
    catch {
        // If URL parsing fails, check the raw string as fallback
        return url.toLowerCase().endsWith('.pdf');
    }
}
//# sourceMappingURL=utils.js.map