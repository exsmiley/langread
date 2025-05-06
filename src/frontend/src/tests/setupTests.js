// Setup file for Jest tests
require('@testing-library/jest-dom');

// Set up internationalization mocks
jest.mock('react-i18next', () => ({
  // this mock makes sure any components using the translate hook can use it without a warning being shown
  useTranslation: () => {
    return {
      t: (str) => str,
      i18n: {
        changeLanguage: () => new Promise(() => {}),
      },
    };
  },
  // mock the Trans component from react-i18next
  Trans: ({ children }) => children,
}));

global.fetch = jest.fn();
global.console.error = jest.fn(); // Silence console errors during tests
