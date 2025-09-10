// Test script to debug login issue
async function testLogin() {
  const baseURL = 'http://localhost:8000/api';
  const credentials = {
    email: 'student1@example.com',
    password: 'password123'
  };

  console.log('🧪 Testing login with credentials:', credentials);
  console.log('🔗 Using API URL:', `${baseURL}/auth/login/`);

  try {
    console.log('📡 Making fetch request...');
    const response = await fetch(`${baseURL}/auth/login/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    });

    console.log('📥 Response received:');
    console.log('- Status:', response.status);
    console.log('- Status Text:', response.statusText);
    console.log('- OK:', response.ok);
    console.log('- Headers:', Object.fromEntries(response.headers.entries()));

    if (!response.ok) {
      console.log('❌ Response not OK, checking error details...');
      
      let errorMessage = 'API request failed';
      try {
        const error = await response.json();
        console.log('📋 Error JSON:', error);
        errorMessage = error.message || error.error || errorMessage;
      } catch (e) {
        console.log('⚠️ Could not parse error as JSON:', e.message);
        const errorText = await response.text();
        console.log('📋 Error text:', errorText);
        errorMessage = response.statusText || errorMessage;
      }
      
      throw new Error(errorMessage);
    }

    const data = await response.json();
    console.log('✅ Success! Response data:', data);
    return data;

  } catch (error) {
    console.error('❌ Login test failed:', error);
    console.error('Error name:', error.name);
    console.error('Error message:', error.message);
    console.error('Error stack:', error.stack);
    
    if (error.name === 'TypeError') {
      console.error('🚨 This is likely a network/CORS issue!');
    }
    
    throw error;
  }
}

// Run the test
testLogin().then(
  (result) => console.log('🎉 Test completed successfully:', result)
).catch(
  (error) => console.log('💥 Test failed with error:', error.message)
);
