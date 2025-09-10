// Debug script to test API connectivity
const fetch = require('node-fetch');

async function testAPI() {
  const baseURL = 'http://localhost:8000/api';
  
  console.log('🔍 Testing API connectivity...');
  console.log('Backend URL:', baseURL);
  
  try {
    // Test 1: Basic connectivity
    console.log('\n1️⃣ Testing basic connectivity...');
    const response1 = await fetch(`${baseURL}/auth/register/`, {
      method: 'OPTIONS',
      headers: {
        'Origin': 'http://localhost:3000',
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type',
      }
    });
    console.log('OPTIONS response status:', response1.status);
    console.log('CORS headers:', {
      'Access-Control-Allow-Origin': response1.headers.get('Access-Control-Allow-Origin'),
      'Access-Control-Allow-Methods': response1.headers.get('Access-Control-Allow-Methods'),
      'Access-Control-Allow-Headers': response1.headers.get('Access-Control-Allow-Headers'),
    });
    
    // Test 2: Registration endpoint
    console.log('\n2️⃣ Testing registration endpoint...');
    const testData = {
      username: 'debuguser',
      email: 'debug@test.com',
      password: 'debugpass123',
      password_confirm: 'debugpass123',
      first_name: 'Debug',
      last_name: 'User',
      role: 'student'
    };
    
    const response2 = await fetch(`${baseURL}/auth/register/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Origin': 'http://localhost:3000'
      },
      body: JSON.stringify(testData)
    });
    
    console.log('Registration response status:', response2.status);
    const responseText = await response2.text();
    console.log('Registration response:', responseText);
    
    if (response2.status === 201) {
      console.log('✅ API is working correctly!');
    } else {
      console.log('❌ API returned error');
    }
    
  } catch (error) {
    console.error('❌ Connection failed:', error.message);
    
    if (error.code === 'ECONNREFUSED') {
      console.log('💡 Solution: Make sure Django server is running on http://localhost:8000');
    } else if (error.message.includes('fetch')) {
      console.log('💡 Solution: Check CORS configuration in Django settings');
    }
  }
}

testAPI();
