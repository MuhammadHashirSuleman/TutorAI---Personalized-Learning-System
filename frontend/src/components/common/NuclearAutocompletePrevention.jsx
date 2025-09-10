import { useEffect } from 'react';

const NuclearAutocompletePrevention = () => {
  useEffect(() => {
    // NUCLEAR OPTION 1: Override all autocomplete at document level
    const nukeAutocomplete = () => {
      // Completely disable autocomplete on ALL inputs
      const style = document.createElement('style');
      style.innerHTML = `
        /* NUCLEAR CSS - Hide everything */
        * {
          -webkit-user-select: none !important;
          -moz-user-select: none !important;
          -ms-user-select: none !important;
          user-select: none !important;
        }
        
        input, textarea {
          -webkit-user-select: text !important;
          -moz-user-select: text !important;
          -ms-user-select: text !important;
          user-select: text !important;
        }

        /* Kill all autocomplete dropdowns */
        input::-webkit-list-button,
        input::-webkit-calendar-picker-indicator,
        input::-webkit-clear-button,
        input::-webkit-inner-spin-button,
        input::-webkit-outer-spin-button,
        input::-webkit-credentials-auto-fill-button,
        input::-webkit-contacts-auto-fill-button {
          display: none !important;
          visibility: hidden !important;
          opacity: 0 !important;
          pointer-events: none !important;
          position: absolute !important;
          right: -9999px !important;
        }

        /* Force no background for autofilled inputs */
        input:-webkit-autofill,
        input:-webkit-autofill:hover,
        input:-webkit-autofill:focus,
        input:-webkit-autofill:active {
          -webkit-animation: autofill-fix 0s forwards;
          -webkit-box-shadow: 0 0 0px 1000px transparent inset !important;
          -webkit-text-fill-color: inherit !important;
          background: transparent !important;
        }

        @-webkit-keyframes autofill-fix {
          to {
            background: transparent !important;
            color: inherit !important;
          }
        }

        /* Hide all possible suggestion containers */
        .pac-container,
        .suggestions,
        .autocomplete-suggestions,
        .ui-autocomplete,
        .tt-menu,
        .dropdown-menu,
        [role="listbox"],
        [role="combobox"] + div,
        div[class*="suggestion"],
        div[class*="autocomplete"],
        div[class*="dropdown"] {
          display: none !important;
          visibility: hidden !important;
          opacity: 0 !important;
          height: 0 !important;
          max-height: 0 !important;
          overflow: hidden !important;
        }

        /* Nuclear option for password managers */
        input[type="email"],
        input[type="password"],
        input[type="text"] {
          font-family: monospace !important;
          font-size: 16px !important; /* Prevents zoom on mobile */
          background-image: none !important;
          background-attachment: scroll !important;
        }

        input[type="email"]:focus,
        input[type="password"]:focus,
        input[type="text"]:focus {
          font-family: inherit !important;
        }
      `;
      document.head.appendChild(style);
    };

    // NUCLEAR OPTION 2: JavaScript intervention
    const interceptAllInputs = () => {
      // Intercept ALL input events
      const inputHandler = (e) => {
        const input = e.target;
        if (input.tagName === 'INPUT') {
          // Force remove any autocomplete attributes added by browser
          input.setAttribute('autocomplete', 'new-password-' + Math.random());
          input.setAttribute('name', 'field-' + Math.random().toString(36));
          
          // Clear any autofilled values immediately
          setTimeout(() => {
            if (input.value && !input.dataset.userTyped) {
              input.value = '';
            }
          }, 0);
        }
      };

      // Monitor for any new inputs being added
      const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          mutation.addedNodes.forEach((node) => {
            if (node.tagName === 'INPUT' || (node.querySelectorAll && node.querySelectorAll('input').length)) {
              const inputs = node.tagName === 'INPUT' ? [node] : node.querySelectorAll('input');
              inputs.forEach(input => {
                input.setAttribute('autocomplete', 'new-password-' + Math.random());
                input.setAttribute('readonly', 'readonly');
                input.addEventListener('focus', () => {
                  input.removeAttribute('readonly');
                }, { once: true });
              });
            }
          });
        });
      });

      observer.observe(document.body, { childList: true, subtree: true });

      // Add event listeners for all input events
      document.addEventListener('input', inputHandler, true);
      document.addEventListener('change', inputHandler, true);
      document.addEventListener('focus', inputHandler, true);
    };

    // NUCLEAR OPTION 3: Override browser APIs
    const overrideBrowserAPIs = () => {
      // Override HTMLInputElement properties
      try {
        const originalValueSetter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
        Object.defineProperty(HTMLInputElement.prototype, 'value', {
          set: function(newValue) {
            // Mark as user-typed if it's being set by user interaction
            if (document.activeElement === this) {
              this.dataset.userTyped = 'true';
            }
            originalValueSetter.call(this, newValue);
          },
          get: function() {
            return this.getAttribute('value') || '';
          }
        });
      } catch (e) {
        console.log('Could not override value setter - browser security prevents it');
      }

      // Disable requestAutocomplete if it exists
      if (HTMLFormElement.prototype.requestAutocomplete) {
        HTMLFormElement.prototype.requestAutocomplete = function() {
          console.log('Autocomplete request blocked');
          return Promise.resolve();
        };
      }
    };

    // NUCLEAR OPTION 4: Clear everything on any focus
    const clearOnFocus = () => {
      document.addEventListener('focusin', (e) => {
        if (e.target.tagName === 'INPUT') {
          // Clear the input immediately on focus
          const originalValue = e.target.value;
          e.target.value = '';
          
          
          // Only restore if user doesn't type within 100ms
          setTimeout(() => {
            if (e.target.value === '') {
              e.target.value = originalValue;
            }
          }, 100);
        }
      }, true);
    };

    // NUCLEAR OPTION 5: Prevent all form-related events
    const preventFormEvents = () => {
      const blockEvents = ['autocomplete', 'autofill', 'input'];
      
      blockEvents.forEach(eventType => {
        document.addEventListener(eventType, (e) => {
          if (e.target.tagName === 'INPUT' && !e.target.dataset.userTyped) {
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();
            return false;
          }
        }, true);
      });
    };

    // Execute all nuclear options
    setTimeout(() => {
      nukeAutocomplete();
      interceptAllInputs();
      overrideBrowserAPIs();
      clearOnFocus();
      preventFormEvents();
    }, 100);

    // Additional extreme measure: Clear inputs every second
    const clearTimer = setInterval(() => {
      document.querySelectorAll('input[autocomplete*="off"], input[data-no-autocomplete="true"]').forEach(input => {
        if (document.activeElement !== input && !input.dataset.userTyped) {
          if (input.value && input.value.includes('@')) {
            // Looks like autofilled email
            input.value = '';
          }
        }
      });
    }, 1000);

    // Cleanup
    return () => {
      clearInterval(clearTimer);
    };
  }, []);

  return null;
};

export default NuclearAutocompletePrevention;
