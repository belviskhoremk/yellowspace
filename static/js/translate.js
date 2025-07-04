// translate.js
async function translateText(text, lang = 'es') {
    try {
        const response = await fetch(`/translate/?text=${encodeURIComponent(text)}&lang=${lang}`);
        const data = await response.json();
        return data.translation || text;
    } catch (error) {
        console.error('Translation error:', error);
        return text; // Fallback to original text
    }
}