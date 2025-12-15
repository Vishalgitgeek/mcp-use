"""HTML template for the main UI."""
def get_index_html() -> str:
    """Get the HTML content for the main page."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Local ↔ Drive Sync</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 600px;
            padding: 30px;
        }
        h1 {
            color: #333;
            margin-bottom: 30px;
            text-align: center;
            font-size: 24px;
        }
        .account-section {
            margin-bottom: 25px;
            display: flex;
            gap: 10px;
            align-items: center;
        }
        select {
            flex: 1;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            background: white;
            cursor: pointer;
        }
        select:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.2s;
        }
        .btn-primary {
            background: #667eea;
            color: white;
        }
        .btn-primary:hover {
            background: #5568d3;
            transform: translateY(-1px);
        }
        .btn-secondary {
            background: #4caf50;
            color: white;
        }
        .btn-secondary:hover {
            background: #45a049;
        }
        .query-section {
            margin-bottom: 25px;
        }
        textarea {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            font-family: inherit;
            resize: vertical;
            min-height: 120px;
        }
        textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        .execute-btn {
            width: 100%;
            padding: 15px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-bottom: 20px;
        }
        .execute-btn:hover {
            background: #5568d3;
        }
        .execute-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .status {
            padding: 12px;
            background: #f5f5f5;
            border-radius: 8px;
            font-size: 14px;
            color: #666;
        }
        .status.loading {
            background: #e3f2fd;
            color: #1976d2;
        }
        .status.error {
            background: #ffebee;
            color: #c62828;
        }
        .status.success {
            background: #e8f5e9;
            color: #2e7d32;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            white-space: pre-wrap;
            font-size: 14px;
            max-height: 400px;
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Local ↔ Drive Sync</h1>
        
        <div class="account-section">
            <select id="accountSelect">
                <option value="">-- Select Account --</option>
            </select>
            <button class="btn-secondary" onclick="addAccount()">+ Add Account</button>
        </div>
        
        <div class="query-section">
            <textarea id="queryInput" placeholder="What do you want to do? (e.g., 'Upload file.txt to Google Drive', 'List files in Drive', 'Download file from Drive')"></textarea>
        </div>
        
        <button class="execute-btn" onclick="executeQuery()" id="executeBtn">Execute</button>
        
        <div class="status" id="status">Ready</div>
        
        <div id="result" class="result" style="display: none;"></div>
    </div>

    <script>
        let accounts = [];

        async function loadAccounts() {
            try {
                const response = await fetch('/api/accounts');
                accounts = await response.json();
                const select = document.getElementById('accountSelect');
                select.innerHTML = '<option value="">-- Select Account --</option>';
                accounts.forEach(email => {
                    const option = document.createElement('option');
                    option.value = email;
                    option.textContent = email;
                    select.appendChild(option);
                });
            } catch (error) {
                console.error('Error loading accounts:', error);
            }
        }

        function addAccount() {
            window.location.href = '/auth/google';
        }

        async function executeQuery() {
            const email = document.getElementById('accountSelect').value;
            const query = document.getElementById('queryInput').value.trim();
            
            if (!email) {
                alert('Please select an account first');
                return;
            }
            
            if (!query) {
                alert('Please enter a query');
                return;
            }

            const statusDiv = document.getElementById('status');
            const resultDiv = document.getElementById('result');
            const executeBtn = document.getElementById('executeBtn');
            
            statusDiv.className = 'status loading';
            statusDiv.textContent = 'Executing...';
            resultDiv.style.display = 'none';
            executeBtn.disabled = true;

            try {
                const response = await fetch('/api/execute', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email, query }),
                });

                const data = await response.json();
                
                if (response.ok) {
                    statusDiv.className = 'status success';
                    statusDiv.textContent = 'Completed';
                    resultDiv.style.display = 'block';
                    resultDiv.textContent = data.result || 'Operation completed successfully';
                } else {
                    statusDiv.className = 'status error';
                    statusDiv.textContent = `Error: ${data.error || 'Unknown error'}`;
                    resultDiv.style.display = 'block';
                    resultDiv.textContent = data.error || 'An error occurred';
                }
            } catch (error) {
                statusDiv.className = 'status error';
                statusDiv.textContent = `Error: ${error.message}`;
                resultDiv.style.display = 'block';
                resultDiv.textContent = error.message;
            } finally {
                executeBtn.disabled = false;
            }
        }

        // Load accounts on page load
        loadAccounts();
    </script>
</body>
</html>"""

