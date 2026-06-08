pipeline {
    agent any 
    stages {
        stage('Build & Compile') {
            steps {
                echo 'Building Docker Image and Compiling C++ Firmware...'
                sh 'docker compose up -d --build'
                sleep 5
            }
        }
        stage('QA: Unit Testing') {
            steps {
                echo 'Verifying ECU logic...'
                sh 'docker exec ecu_monitor_live python3 backend/tests/ecu_test.py'
            }
        }
        stage('QA: Integration Testing') {
            steps {
                echo 'Checking API Connectivity...'
                sh 'docker exec ecu_monitor_live pytest backend/tests/test_api.py -v --junitxml=api_results.xml'
                sh 'docker cp ecu_monitor_live:/app/api_results.xml .'
            }
            post {
                always {
                    junit 'api_results.xml'
                }
            }
        }
        stage('QA: Validation Matrix') {
            steps {
                script {
                    def modes = ['STRICT', 'BROKEN', 'SIMULATION']
        
                    for (int i = 0; i < modes.size(); i++) {
                        def currentM = modes[i]
                        
                        echo "--- Running Tests for Mode: ${currentM} ---"
                        sh "docker exec -e ECU_MODE=${currentM} ecu_monitor_live pytest backend/tests/test_ecu.py -v --target-url=http://localhost:8001 --junitxml=${currentM}_results.xml"
                        sh "docker cp ecu_monitor_live:/app/${currentM}_results.xml ."
                    }
                }
            }
            post {
                always {
                    junit '*_results.xml'
                    
                    // Pull the final SQLite DB state out of the container for analysis
                    sh 'docker cp ecu_monitor_live:/app/backend/ecu_history.db .'
                    archiveArtifacts artifacts: 'ecu_history.db, *.xml', allowEmptyArchive: true
                }
            }
        }

        // --- 🛠️ NEW STAGE ADDED HERE ---
        stage('QA: Analyze DB System Defects') {
            steps {
                echo 'Analyzing SQLite Database Logs for System Defects...'
                // Run an inline Python script to query the database file we just copied out
                sh '''
                python3 -c "
import sqlite3
try:
    conn = sqlite3.connect('ecu_history.db')
    cursor = conn.cursor()
    
    # Check total rows logged
    total = cursor.execute('SELECT count(*) FROM logs').fetchone()[0]
    # Check how many actual sensor errors were captured
    errors = cursor.execute(\\"SELECT count(*) FROM logs WHERE status='SENSOR ERROR'\\").fetchone()[0]
    
    print('\\n===================================')
    print('=== INTEGRATION DATABASE REPORT ===')
    print(f'Total Telemetry Packets Logged: {total}')
    print(f'Total Hardware Defects Identified: {errors}')
    print('===================================')
    
    conn.close()
except Exception as e:
    print(f'Database analysis failed: {e}')
"
                '''
            }
        }
    } // End of stages block

    // --- 🛠️ GLOBAL POST CLEANUP BLOCK ---
    // This runs after EVERY single stage finishes, ensuring the build agent is left pristine.
    post {
        always {
            echo 'Cleaning up the Integration Environment...'
            sh 'docker compose down --volumes --remove-orphans'
        }
    }
}