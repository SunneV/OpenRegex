// static/js/components/output/hoverHighlight.js

export const attachMatchEventListeners = () => {
  // Store clicked/memorized highlights for class: 'match-x-group-y'
  let memorizedHighlights = new Set();

  // Helper function to highlight/unhighlight a group
  const toggleHighlight = (elements, shouldHighlight) => {
    elements.forEach(el => {
      if (shouldHighlight) {
        if (!memorizedHighlights.has(el)) {
          el.classList.add('highlight');
        }
      } else {
        if (!memorizedHighlights.has(el)) {
          el.classList.remove('highlight');
        }
      }
    });
  };

  document.addEventListener('mouseover', (event) => {
    const elementUnderMouse = event.target;

    // Check for match-x-group-y (x and y are numbers)
    let match = elementUnderMouse.className.match(/match-(\d+)-group-(\d+)/);
    if (match) {
      const xValue = match[1];
      const yValue = match[2];
      const elementsToHighlight = document.querySelectorAll(`.match-${xValue}-group-${yValue}, .regex-highlight.color-${yValue}`);
      toggleHighlight(elementsToHighlight, true);
    }

    // Check for match-x (x is a number)
    match = elementUnderMouse.className.match(/match-(\d+)$/);
    if (match) {
      const xValue = match[1];
      const elementsToHighlight = document.querySelectorAll(`.match-${xValue}`);
      toggleHighlight(elementsToHighlight, true);
    }

    // Check for regex-highlight color-x (x is a number)
    match = elementUnderMouse.className.match(/regex-highlight color-(\d+)$/);
    if (match) {
      const xValue = match[1];
      const elementsToHighlight = document.querySelectorAll(`.color-${xValue}`);
      toggleHighlight(elementsToHighlight, true);
    }
  });

  document.addEventListener('mouseout', (event) => {
    const elementBeingLeft = event.target;

    // Check for match-x-group-y (x and y are numbers)
    let match = elementBeingLeft.className.match(/match-(\d+)-group-(\d+)/);
    if (match) {
      const xValue = match[1];
      const yValue = match[2];
      const elementsToUnhighlight = document.querySelectorAll(`.match-${xValue}-group-${yValue}, .regex-highlight.color-${yValue}`);
      toggleHighlight(elementsToUnhighlight, false);
    }

    // Check for match-x (x is a number)
    match = elementBeingLeft.className.match(/match-(\d+)/);
    if (match) {
      const xValue = match[1];
      const elementsToUnhighlight = document.querySelectorAll(`.match-${xValue}`);
      toggleHighlight(elementsToUnhighlight, false);
    }

    // Check for regex-highlight color-x (x is a number)
    match = elementBeingLeft.className.match(/regex-highlight color-(\d+)/);
    if (match) {
      const xValue = match[1];
      const elementsToUnhighlight = document.querySelectorAll(`.color-${xValue}`);
      toggleHighlight(elementsToUnhighlight, false);
    }
  });

  document.addEventListener('click', (event) => {
    const clickedElement = event.target;

    // Check for match-x-group-y (x and y are numbers)
    let match = clickedElement.className.match(/match-(\d+)-group-(\d+)/);
    if (match) {
      const xValue = match[1];
      const yValue = match[2];
      const elementsInGroup = document.querySelectorAll(`.match-${xValue}-group-${yValue}, .regex-highlight.color-${yValue}`);
      elementsInGroup.forEach(el => {
        if (memorizedHighlights.has(el)) {
          memorizedHighlights.delete(el);
          el.classList.remove('highlight');
        } else {
          memorizedHighlights.add(el);
          el.classList.add('highlight');
        }
      });
    } else {
      // Check for match-x (x is a number)
      match = clickedElement.className.match(/match-(\d+)/);
      if (match) {
        const xValue = match[1];
        const elementsToMemorize = document.querySelectorAll(`.match-${xValue}`);
        elementsToMemorize.forEach(el => {
          if (memorizedHighlights.has(el)) {
            memorizedHighlights.delete(el);
            el.classList.remove('highlight');
          } else {
            memorizedHighlights.add(el);
            el.classList.add('highlight');
          }
        });
      } else {
        // Check for regex-highlight color-x (x is a number)
        match = clickedElement.className.match(/regex-highlight color-(\d+)/);
        if (match) {
          const xValue = match[1];
          const elementsToMemorize = document.querySelectorAll(`.color-${xValue}`);
          elementsToMemorize.forEach(el => {
            if (memorizedHighlights.has(el)) {
              memorizedHighlights.delete(el);
              el.classList.remove('highlight');
            } else {
              memorizedHighlights.add(el);
              el.classList.add('highlight');
            }
          });
        } else {
            // Clicked outside of any relevant element, clear all memorized highlights
            memorizedHighlights.forEach(el => {
              el.classList.remove('highlight');
            });
            memorizedHighlights.clear();
        }
      }
    }
  });
};