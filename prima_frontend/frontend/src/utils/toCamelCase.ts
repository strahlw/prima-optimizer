// Utility function to convert snake_case to camelCase
export function toCamelCase(str: string) {
    return str.replace(/_([a-z])/g, (match, p1) => p1.toUpperCase());
}

export function stringToCamelCase(str: string) {
    return str
        .toLowerCase()
        .replace(/[^a-zA-Z0-9 ]/g, '')
        .split(' ')
        .map((word, index) => {
            if (index === 0) return word;
            return word.charAt(0).toUpperCase() + word.slice(1);
        })
        .join('');
}

// Function to convert object keys to camelCase
export function keysToCamelCase(obj: { [key: string]: any }): any {
    if (Array.isArray(obj)) {
        return obj.map((v) => keysToCamelCase(v));
    } else if (obj !== null && obj.constructor === Object) {
        return Object.keys(obj).reduce(
            (result, key) => {
                result[toCamelCase(key)] = keysToCamelCase(obj[key]);
                return result;
            },
            {} as { [key: string]: any }
        );
    }
    return obj;
}
