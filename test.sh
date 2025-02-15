#!/bin/bash

# Number of iterations
RUNS=8

# Paths to scripts
SERVER_SCRIPT="server.py"
STUDENT_SCRIPT="student.py"

# Log file
LOG_FILE="snake_run_logs.txt"

# Ensure the log file is empty
> "$LOG_FILE"

# Function to check if the server is ready
check_server_ready() {
    local retries=5
    local wait=2
    for _ in $(seq 1 $retries); do
        # Check if the server is listening
        nc -z 127.0.0.1 8000 && return 0
        echo "Waiting for server to start..."
        sleep $wait
    done
    return 1
}

echo "Starting $RUNS runs of the Snake game..."

for i in $(seq 1 $RUNS); do
    echo "Run $i: Starting server and student..." | tee -a "$LOG_FILE"

    # Start the server in the background
    python3 $SERVER_SCRIPT &
    SERVER_PID=$!

    # Wait for the server to be ready
    if ! check_server_ready; then
        echo "Run $i: Server failed to start. Skipping..." | tee -a "$LOG_FILE"
        kill $SERVER_PID
        continue
    fi

    # Run student.py and capture output
    python3 $STUDENT_SCRIPT > temp_output.log
    STUDENT_EXIT=$?

    SCORE=$(grep -oP 'Score:\s+\K\d+' temp_output.log | tail -1)

    # Kill the server
    kill $SERVER_PID

    if [[ $STUDENT_EXIT -ne 0 ]]; then
        echo "Run $i: student.py encountered an error. Check temp_output.log." | tee -a "$LOG_FILE"
        continue
    fi

    # Extract the number of steps and score
    STEPS=$(grep -oP '\[\K\d+(?=\])' temp_output.log | tail -1)

    echo "Run $i: Steps = $STEPS, Score = $SCORE" | tee -a "$LOG_FILE"

    # Clean up temporary log
    rm -f temp_output.log
done

echo "All runs completed. Check $LOG_FILE for results."
