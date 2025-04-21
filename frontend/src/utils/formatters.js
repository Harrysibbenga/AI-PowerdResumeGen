/**
 * Format a date to a readable string (e.g., "Jan 2023")
 * @param {string|Date} date - Date to format
 * @returns {string} - Formatted date string
 */
export function formatDate(date) {
  if (!date) return '';
  
  try {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return dateObj.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short'
    });
  } catch (e) {
    console.error('Error formatting date:', e);
    return String(date);
  }
}

/**
 * Format a timestamp from Firestore
 * @param {Object|number} timestamp - Firestore timestamp or Unix timestamp
 * @returns {string} - Formatted date string
 */
export function formatTimestamp(timestamp) {
  if (!timestamp) return '';
  
  try {
    if (timestamp && typeof timestamp.toDate === 'function') {
      return formatDate(timestamp.toDate());
    }
    if (typeof timestamp === 'number') {
      return formatDate(new Date(timestamp * 1000));
    }
    return formatDate(timestamp);
  } catch (e) {
    console.error('Error formatting timestamp:', e);
    return '';
  }
}

/**
 * Capitalize the first letter of each word
 * @param {string} text - Text to capitalize
 * @returns {string} - Capitalized text
 */
export function capitalize(text) {
  if (!text) return '';
  return text
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

/**
 * Format currency
 * @param {number} amount - Amount to format
 * @param {string} currency - Currency code (default: GBP)
 * @returns {string} - Formatted currency
 */
export function formatCurrency(amount, currency = 'GBP') {
  if (typeof amount !== 'number') return '';
  return new Intl.NumberFormat('en-GB', {
    style: 'currency',
    currency
  }).format(amount);
}

/**
 * Format a name as initials
 * @param {string} name - Full name
 * @returns {string} - Initials
 */
export function getInitials(name) {
  if (!name) return '';
  return name
    .split(' ')
    .map(part => part.charAt(0))
    .join('')
    .toUpperCase();
}

/**
 * Split text into bullet points
 * @param {string} text - Text potentially containing multiple bullet points
 * @returns {string[]} - Array of bullet point strings
 */
export function splitBulletPoints(text) {
  if (!text) return [];
  const bullets = [];
  for (const line of text.split('\n')) {
    const trimmed = line.trim();
    if (trimmed) {
      let cleanLine = trimmed;
      if (trimmed.startsWith('•') || trimmed.startsWith('-') || trimmed.startsWith('*')) {
        cleanLine = trimmed.substring(1).trim();
      }
      bullets.push(cleanLine);
    }
  }
  return bullets;
}

/**
 * Format a file size in bytes to a human-readable string
 * @param {number} bytes - File size in bytes
 * @returns {string} - Formatted file size
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${parseFloat((bytes / Math.pow(1024, i)).toFixed(2))} ${sizes[i]}`;
}

/**
 * Truncate text to a specific length
 * @param {string} text - Text to truncate
 * @param {number} max - Max length before cutting
 * @returns {string} - Truncated text with ellipsis
 */
export function truncateText(text, max = 100) {
  if (!text) return '';
  return text.length > max ? text.slice(0, max) + '...' : text;
}
