// Test script to debug the resume data initialization
const { defaultForm } = require('./frontend/src/utils/defaultForm.js');

console.log('=== TEST DEBUG ===');
console.log('defaultForm structure:');
console.log('- title:', JSON.stringify(defaultForm.title));
console.log('- targetJobTitle:', JSON.stringify(defaultForm.targetJobTitle));
console.log('- fullName:', JSON.stringify(defaultForm.fullName));

// Test what happens if properties are missing
const testData = { ...defaultForm };
delete testData.title;
console.log('\nAfter deleting title:');
console.log('- title:', JSON.stringify(testData.title));
console.log('- title || "":', JSON.stringify(testData.title || ''));

// Test normalization logic
const normalizeTest = (data) => {
  return {
    title: data.title || '',
    targetJobTitle: data.targetJobTitle || ''
  };
};

console.log('\nNormalization test:');
console.log('With data:', normalizeTest(defaultForm));
console.log('With missing title:', normalizeTest(testData));
console.log('With null:', normalizeTest({ title: null, targetJobTitle: 'test' }));