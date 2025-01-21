// static/js/components/regexInput.js
import { getElement } from '../utils/dom.js';
import { handleInputChange } from '../main.js';

const regexInput = getElement('regex-input');

export const initRegexInput = () => {
  regexInput.addEventListener('input', handleInputChange);
};

export const getRegexInputValue = () => regexInput.value;