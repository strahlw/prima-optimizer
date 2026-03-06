export function convertKeyToLabel(key: string | number) {
    key = key.toString();
    // Insert spaces before capital letters and split words
    const words = key.replace(/([A-Z])/g, ' $1').trim();

    // Capitalize the first letter of each word
    return words
        .split(' ') // Split into an array of words
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()) // Capitalize first letter
        .join(' '); // Join words back with spaces
}
