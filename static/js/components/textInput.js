// static/js/components/textInput.js
import { getElement } from '../utils/dom.js';
import { handleInputChange } from '../main.js';

const textInput = getElement('text-input');

export const initTextInput = () => {
  textInput.addEventListener('input', handleInputChange);
};

export const getTextInputValue = () => textInput.value;