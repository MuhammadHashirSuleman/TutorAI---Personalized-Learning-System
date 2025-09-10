import React, { useState, useRef } from 'react';
import { 
  Box, 
  InputLabel, 
  InputAdornment, 
  IconButton,
  FormControl,
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';

const StealthPasswordInput = ({ 
  label = "Password", 
  value = "", 
  onChange, 
  fullWidth = true,
  required = false,
  margin = "normal",
  sx = {}
}) => {
  const [showPassword, setShowPassword] = useState(false);
  const [focused, setFocused] = useState(false);
  const inputRef = useRef(null);

  const handleInputChange = (e) => {
    const newValue = e.target.textContent || e.target.innerText || '';
    onChange({ target: { name: 'password', value: newValue } });
  };

  const handleKeyDown = (e) => {
    // Allow normal text editing
    if (e.key === 'Enter') {
      e.preventDefault();
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const paste = (e.clipboardData || window.clipboardData).getData('text');
    const newValue = value + paste;
    onChange({ target: { name: 'password', value: newValue } });
  };

  const displayValue = showPassword ? value : '•'.repeat(value.length);

  return (
    <FormControl 
      fullWidth={fullWidth} 
      margin={margin}
      sx={{
        ...sx,
        '& .custom-input': {
          width: '100%',
          height: '56px',
          border: `1px solid ${focused ? '#1976d2' : 'rgba(0, 0, 0, 0.23)'}`,
          borderRadius: '4px',
          padding: '16px 14px',
          fontFamily: 'inherit',
          fontSize: '16px',
          outline: 'none',
          backgroundColor: 'transparent',
          position: 'relative',
          display: 'flex',
          alignItems: 'center',
          cursor: 'text',
          transition: 'border-color 0.2s',
          '&:hover': {
            borderColor: focused ? '#1976d2' : 'rgba(0, 0, 0, 0.87)',
          }
        }
      }}
    >
      <InputLabel 
        shrink 
        sx={{ 
          position: 'absolute',
          top: focused || value ? '-9px' : '16px',
          left: '14px',
          fontSize: focused || value ? '12px' : '16px',
          color: focused ? '#1976d2' : 'rgba(0, 0, 0, 0.6)',
          backgroundColor: 'white',
          padding: '0 4px',
          transition: 'all 0.2s',
          zIndex: 1,
          pointerEvents: 'none',
        }}
      >
        {label} {required && '*'}
      </InputLabel>
      
      <Box className="custom-input">
        {/* Hidden real input for form submission */}
        <input
          type="hidden"
          name={`realpassword_${Date.now()}`}
          value={value}
          data-not-password="true"
          data-lpignore="true"
          data-1p-ignore="true"
          data-bitwarden-watching="1"
        />
        
        {/* Fake visible input that browsers can't recognize */}
        <div
          ref={inputRef}
          contentEditable
          suppressContentEditableWarning
          onInput={handleInputChange}
          onKeyDown={handleKeyDown}
          onPaste={handlePaste}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          style={{
            flex: 1,
            border: 'none',
            outline: 'none',
            fontFamily: 'monospace',
            fontSize: '16px',
            letterSpacing: showPassword ? 'normal' : '2px',
            color: 'inherit',
            backgroundColor: 'transparent',
            minHeight: '24px',
            cursor: 'text',
          }}
          data-not-input="true"
          data-no-autocomplete="true"
          data-lpignore="true"
          data-1p-ignore="true"
          data-bitwarden-watching="1"
        >
          {displayValue}
        </div>

        <InputAdornment position="end">
          <IconButton
            onClick={() => setShowPassword(!showPassword)}
            edge="end"
            size="small"
          >
            {showPassword ? <VisibilityOff /> : <Visibility />}
          </IconButton>
        </InputAdornment>
      </Box>
    </FormControl>
  );
};

export default StealthPasswordInput;
