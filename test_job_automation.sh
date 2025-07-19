#!/bin/bash
# Test job automation fix

echo "Testing CCMaster Job Automation..."
echo "=================================="

# Find a designer session
DESIGNER_SESSION=$(ls ~/.ccmaster/job_queue | grep -E "designer|mcp_" | head -1)

if [ -z "$DESIGNER_SESSION" ]; then
    echo "No session found with job queue. Please ensure CCMaster is watching sessions."
    exit 1
fi

echo "Found session: $DESIGNER_SESSION"
echo ""

# Create a test job
JOB_ID="job_test_$(date +%s)"
JOB_FILE="$HOME/.ccmaster/job_queue/$DESIGNER_SESSION/$JOB_ID.json"

mkdir -p "$HOME/.ccmaster/job_queue/$DESIGNER_SESSION"

cat > "$JOB_FILE" <<EOF
{
  "id": "$JOB_ID",
  "title": "Test Automated Job Execution",
  "description": "This is a test job to verify automation is working. Please type 'echo Job automation is working!' and then mark this job as complete.",
  "priority": "p0",
  "status": "pending",
  "created_by": "test_script",
  "created_by_identity": "tester",
  "assigned_to": "$DESIGNER_SESSION",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S.%NZ)"
}
EOF

echo "Created test job: $JOB_ID"
echo "Job file: $JOB_FILE"
echo ""
echo "Now monitoring job status..."
echo "If automation is working, the job should change from 'pending' to 'doing' within 20 seconds."
echo ""

# Monitor job status for 30 seconds
for i in {1..30}; do
    if [ -f "$JOB_FILE" ]; then
        STATUS=$(jq -r '.status' "$JOB_FILE" 2>/dev/null)
        echo -ne "\rCheck $i/30: Job status = $STATUS    "
        
        if [ "$STATUS" = "doing" ]; then
            echo -e "\n\n✅ SUCCESS! Job automation is working - job was picked up and is being executed."
            echo ""
            echo "Check the terminal window for session $DESIGNER_SESSION to see the job prompt."
            exit 0
        fi
    else
        echo -e "\n\n❌ Job file disappeared unexpectedly!"
        exit 1
    fi
    sleep 1
done

echo -e "\n\n❌ FAILED: Job was not picked up after 30 seconds."
echo "Job is still in 'pending' status."
echo ""
echo "Troubleshooting:"
echo "1. Make sure CCMaster is running with 'ccmaster watch'"
echo "2. Check that the session $DESIGNER_SESSION is idle"
echo "3. Check logs at ~/.ccmaster/logs/${DESIGNER_SESSION}.log"

exit 1