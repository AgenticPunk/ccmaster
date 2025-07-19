# PM Mode Usage Guide

PM (Project Manager) Mode is a new feature in CCMaster that enables true team collaboration by allowing Claude to analyze a project description, automatically create specialized Claude instances, and coordinate their work as a unified team.

> **Note**: CCMaster now uses a file-based approach for sending prompts to Claude instances, eliminating input method conflicts. This ensures reliable prompt delivery even with Chinese or other non-ASCII input methods.

## Key Features: True Team Collaboration

- **Shared Workspace**: All team members work in the same directory
- **Real-time Coordination**: PM can send tasks to any team member at any time
- **Dynamic Task Assignment**: PM responds to progress and assigns new tasks accordingly
- **Unified Monitoring**: See all team members' status in one view
- **Inter-session Communication**: Team members share files and can see each other's work

## How It Works

1. **Project Analysis**: A PM Claude instance analyzes your project description
2. **Team Creation**: PM uses MCP tools to create specialized team members
3. **Task Distribution**: PM assigns initial tasks to each team member
4. **Continuous Coordination**: PM monitors progress and sends new tasks as needed
5. **Dynamic Team Growth**: Add new requirements to PM anytime to expand the team
6. **Unified Monitoring**: All instances are monitored together with auto-continue support

## Usage

### Basic Command
```bash
ccmaster pm "Create an e-commerce website with React frontend, Node.js backend, and PostgreSQL database"
```

### With Options
```bash
# Disable watch mode for created instances
ccmaster pm "Your project description" --no-watch

# Use a custom PM prompt template
ccmaster pm "Your project description" --pm-template /path/to/template.md

# Specify working directory
ccmaster pm "Your project description" -d /path/to/project
```

## Team Collaboration in Action

PM Mode enables true team collaboration through MCP tools. Each team member has access to collaboration tools and can communicate directly with other team members:

### Creating Collaborative Team Members
PM Claude creates team members with full collaboration capabilities:
```
/mcp__ccmaster__create_session working_dir="." watch_mode=true role="Frontend Developer" initial_prompt="You are a Frontend Developer specializing in React, part of a collaborative development team.

TEAM COLLABORATION TOOLS:
- /mcp__ccmaster__get_team_info - See all team members and their roles
- /mcp__ccmaster__send_message_to_session - Communicate with specific team members
- /mcp__ccmaster__broadcast_to_team - Update the entire team
- /mcp__ccmaster__wait_for_dependency - Wait for dependencies from other team members
- /mcp__ccmaster__notify_completion - Notify when you complete important components

Your task: Create the user interface components..."
```

### Sending Tasks to Team Members
PM can send specific tasks to any team member:
```
/mcp__ccmaster__send_message_to_session session_id="20250119_143022_123456" message="Please implement the shopping cart component" wait_for_response=true
```

### Coordinating Multiple Team Members
PM can assign related tasks to multiple team members simultaneously:
```
/mcp__ccmaster__coordinate_sessions task_description="Implement user authentication" session_assignments='{"session_1": "Create login UI", "session_2": "Build auth API"}'
```

### Monitoring Team Progress
PM can check the status of any team member:
```
/mcp__ccmaster__get_session_status session_id="20250119_143022_123456"
```

### Dynamic Task Assignment
As team members complete tasks, PM can assign new ones:
```
PM: "Frontend dev completed the cart. Now assigning checkout flow..."
/mcp__ccmaster__send_message_to_session session_id="frontend_session" message="Great work! Now implement the checkout process"
```

### Direct Team Member Communication
Team members can communicate directly without going through PM:
```
# Frontend Developer needs API endpoint
Frontend: /mcp__ccmaster__send_message_to_session session_id="backend_dev_id" message="I need an API endpoint for product search. Can you create GET /api/products/search?q=query?"

# Backend Developer responds
Backend: /mcp__ccmaster__send_message_to_session session_id="frontend_dev_id" message="Product search API is ready at GET /api/products/search. It returns {products: [...], total: n}"

# Designer broadcasts update to all
Designer: /mcp__ccmaster__broadcast_to_team message="Updated color scheme: primary=#007bff, secondary=#6c757d. Please update your components." sender_role="UI Designer"
```

### Managing Dependencies
Team members handle dependencies intelligently:
```
# Frontend waiting for Backend
Frontend: /mcp__ccmaster__wait_for_dependency dependency_session="backend_dev_id" dependency_description="User authentication API endpoints" timeout=300

# Backend completes and notifies
Backend: /mcp__ccmaster__notify_completion task_description="User authentication API" output_details="Created endpoints: POST /api/login, POST /api/logout, POST /api/register, GET /api/user/profile"
```

## Alternative: JSON Output (Backup Method)
PM Claude can also output a JSON configuration that CCMaster monitors:
```json
{
  "roles": [
    {
      "title": "Frontend Developer",
      "count": 1,
      "initial_prompt": "You are a frontend developer specializing in React..."
    }
  ]
}
```

## Continuous Team Management

PM Mode now supports continuous operation:

1. **No Timeout**: PM Claude runs indefinitely (no 5-minute limit)
2. **Add Requirements Anytime**: Type new requirements in the PM terminal window
3. **Automatic Instance Creation**: Each new JSON output creates additional instances
4. **Dynamic Team Growth**: Your team grows as your project evolves

### Example: Growing Your Team

```bash
# Initial command
ccmaster pm "Create a blog platform"

# PM creates: Frontend Dev, Backend Dev

# Later in PM terminal, you type:
"Add a mobile app for iOS and Android"

# PM outputs new JSON and creates: iOS Developer, Android Developer

# Even later:
"We need real-time analytics and monitoring"

# PM creates: Data Engineer, DevOps Engineer
```

### PM Session Behavior

- **PM Terminal Always Active**: The PM Claude terminal window remains active throughout
- **No Auto-Continue**: PM session never receives auto-continue (only worker sessions do)
- **Manual Input Only**: You must manually type new requirements in the PM terminal
- **Exit Control**: When PM session ends, all worker sessions are gracefully terminated

## Example Workflow: Real Team Collaboration

1. Run the PM command:
```bash
ccmaster pm "Build a real-time chat application with user authentication"
```

2. PM Claude analyzes and creates the team:
```
Based on the project requirements, I'll create the optimal team composition.

Creating Frontend Developer...
/mcp__ccmaster__create_session working_dir="." watch_mode=true initial_prompt="You are a Frontend Developer specializing in React. Create a real-time chat UI with user authentication forms..."

Creating Backend Developer...
/mcp__ccmaster__create_session working_dir="." watch_mode=true initial_prompt="You are a Backend Developer specializing in Node.js. Implement WebSocket server and authentication APIs..."

Creating DevOps Engineer...
/mcp__ccmaster__create_session working_dir="." watch_mode=true initial_prompt="You are a DevOps Engineer. Set up Docker containers and deployment pipeline..."

Team creation complete! I've created 3 specialized Claude instances to work on your project.
```

3. PM coordinates the team's work:
```
# PM checks frontend progress
/mcp__ccmaster__get_session_status session_id="20250119_143022_123456"
> Status: Working on login component

# PM assigns coordinated tasks
/mcp__ccmaster__coordinate_sessions task_description="Implement real-time messaging" session_assignments='{"20250119_143022_123456": "Create chat UI with message list and input", "20250119_143025_789012": "Implement WebSocket handlers for messages"}'

# PM responds to completion
Frontend: "Login UI complete with form validation"
PM: /mcp__ccmaster__send_message_to_session session_id="20250119_143022_123456" message="Excellent! Now integrate the chat UI with the WebSocket connection that Backend is creating"
```

4. PM handles errors and coordinates fixes:
```
# PM tests the project
PM: "All team members have completed initial implementation. Let me test the project..."
> npm start
> Error: Module not found: Can't resolve './components/UserAuth'

# PM assigns the error to the responsible team member
PM: /mcp__ccmaster__send_message_to_session session_id="frontend_dev" message="Frontend error detected: Missing UserAuth component. Error: Module not found './components/UserAuth'. Please create this component or fix the import path."

# Frontend fixes the issue
Frontend: "Fixed! UserAuth component was in auth/ subdirectory. Updated import path."

# PM retests
PM: "Testing again after frontend fix..."
> npm start
> Error: API connection failed: ECONNREFUSED 127.0.0.1:3000

# PM assigns to backend
PM: /mcp__ccmaster__send_message_to_session session_id="backend_dev" message="Backend not running on port 3000. Please ensure the API server is configured and can be started with 'npm run server'."

# Iterative fixing continues until project runs successfully
```

5. Real-time monitoring shows team activity:
```
[PM][14:30:22] ● Processing
[1][14:30:25] ● Working → Using Write (creating LoginForm.jsx)
[2][14:30:26] ● Working → Using Write (creating auth.controller.js)
[3][14:30:27] ● Working → Using Write (creating Dockerfile)
[PM][14:31:00] → Sending task to Frontend Developer
[1][14:31:02] ● Processing new task from PM
[2][14:31:05] ▶ Auto-continue
```

6. Dynamic team expansion:
```
# User types in PM terminal:
"We need to add video chat functionality"

# PM responds:
"Adding video chat requires specialized expertise. Creating additional team members..."

/mcp__ccmaster__create_session working_dir="." watch_mode=true initial_prompt="You are a WebRTC Specialist. Implement peer-to-peer video chat..."

# PM coordinates with existing team:
/mcp__ccmaster__send_message_to_session session_id="frontend_dev" message="New team member joining for video chat. Please prepare UI space for video elements"
```

7. True collaboration in action:
   - All team members work in the same directory
   - Frontend creates `components/VideoChat.jsx`
   - WebRTC specialist can immediately see and integrate with it
   - Backend extends API to support video signaling
   - PM monitors and coordinates all activities

8. Complete project lifecycle management:
```
# Initial development
PM: "Team, let's build the chat application. Frontend, start with UI. Backend, set up API."

# Integration phase
PM: "Frontend and Backend, your components are ready. Let's integrate."
/mcp__ccmaster__coordinate_sessions task_description="Integration phase" session_assignments='{"frontend": "Connect to WebSocket API", "backend": "Enable CORS and test endpoints"}'

# Testing and error resolution
PM: "Running integration tests..."
> npm test
> FAIL: Authentication flow broken
PM: /mcp__ccmaster__send_message_to_session session_id="frontend" message="Auth test failing: 'Login button not triggering API call'. Please check LoginForm component event handlers."

# Deployment preparation
PM: "All tests passing! Preparing for deployment."
/mcp__ccmaster__coordinate_sessions task_description="Deployment preparation" session_assignments='{"frontend": "Build production bundle", "backend": "Set production configs", "devops": "Prepare Docker containers"}'

# Final validation
PM: "Running final production build..."
> npm run build && npm run start:prod
> ✓ Application running on port 3000
PM: "Excellent work team! Project is ready for deployment."
```

## Custom PM Templates

Create a custom template file to customize how PM Claude analyzes projects:

```markdown
# pm_template.md
You are an expert project manager. Analyze the project and create a team.

Consider:
- Frontend complexity
- Backend requirements
- Database needs
- Testing requirements
- Documentation needs

Output a JSON configuration with roles...
```

Then use:
```bash
ccmaster pm "Your project" --pm-template pm_template.md
```

## Features

- **True Team Collaboration**: All team members work together in a shared workspace
- **Real-time Task Assignment**: PM can send tasks to any team member at any time
- **Dynamic Coordination**: PM responds to progress and coordinates team efforts
- **Shared Context**: Team members see each other's files and can build on each other's work
- **Automatic MCP Setup**: MCP server enables inter-session communication
- **Watch Mode Control**: Press [w] to toggle watch mode for all worker sessions (PM excluded)
- **Unified Monitoring**: See all sessions in one view with clear prefixes
- **Session Persistence**: All sessions tracked in ~/.ccmaster/sessions.json
- **Graceful Shutdown**: Press [q] to stop all sessions cleanly
- **Continuous Operation**: PM Claude runs indefinitely, no timeout
- **Dynamic Team Building**: Add team members anytime by providing new requirements

## Team Collaboration FAQ

**Q: Do the created Claude instances actually work together as a team?**
A: Yes! CCMaster's PM mode enables true team collaboration:
- All instances work in the same directory (shared workspace)
- PM can send tasks to specific team members or coordinate multiple members
- Team members see each other's files and can integrate their work
- PM continuously monitors and coordinates the team based on progress

**Q: Can the PM send new requirements to team members?**
A: Absolutely! The PM uses MCP tools to:
- Send specific tasks: `/mcp__ccmaster__send_message_to_session`
- Coordinate multiple members: `/mcp__ccmaster__coordinate_sessions`
- Check progress: `/mcp__ccmaster__get_session_status`
- Dynamically assign new tasks based on completion

**Q: How do team members respond to PM's temporary requirements?**
A: Team members receive tasks from PM and work on them immediately:
- PM sends task → Team member processes it → Updates shared files
- Other team members can see the changes and build upon them
- PM monitors progress and sends follow-up tasks as needed

**Q: How does PM handle errors when running the project?**
A: PM follows a systematic error handling workflow:
1. Runs the project using appropriate commands (npm start, python app.py, etc.)
2. Analyzes any errors that occur
3. Identifies which team member should fix each error
4. Sends detailed error information to the responsible developer
5. Waits for fixes and retests
6. Iterates until all errors are resolved
7. Coordinates deployment when everything works correctly

## Tips

1. **Be Specific**: Provide detailed project descriptions for better role definitions
2. **Iterative Development**: Start simple, add complexity through new requirements
3. **Let PM Test**: PM will run and test your project, identifying and assigning errors
4. **Trust the Process**: PM knows which team member should fix each type of error
5. **Monitor Progress**: Watch the real-time status to see team collaboration in action
6. **Team Evolution**: Use PM terminal to evolve your team as project needs change
7. **Deployment Ready**: PM ensures the project works before coordinating deployment

## Limitations

- JSON must be in markdown code block with ```json
- PM session doesn't get auto-continue (only worker sessions do)
- All instances share the same working directory
- Duplicate JSON configurations are ignored (prevents accidental re-creation)

## Troubleshooting

### PM Claude Shows as Idle
This is normal! PM Claude uses MCP tools to create instances, which happens quickly. After creating instances, PM returns to idle state waiting for new instructions.

### If Instances Aren't Created
1. **Check MCP Server**: Ensure MCP server is running (look for "MCP Server running on port" message)
2. **Verify MCP Tools**: PM Claude should use `/mcp__ccmaster__create_session` commands
3. **JSON Fallback**: If using JSON output, ensure it's in markdown code block with ```json
4. **Check Logs**: Look for error messages prefixed with [PM] in CCMaster output

### Technical Details

- Prompts are sent via `cat` command from temporary files (avoids input method issues)
- Automatic submission using `do script ""` command (sends Enter key)
- No dependency on clipboard or keyboard simulation
- Works correctly regardless of system input method (Chinese, Japanese, etc.)
- PM Claude primarily uses MCP tools for instance creation (immediate effect)
- JSON monitoring is a backup method (checks ~/.ccmaster/logs/ and ~/.claude/SESSION_ID/logs/)
- New instances appear with incrementing indices ([1], [2], etc.)
- PM session never receives auto-continue commands
- Monitor runs quietly in background, only reporting when JSON blocks are found
- Temporary files are cleaned up after 10 seconds