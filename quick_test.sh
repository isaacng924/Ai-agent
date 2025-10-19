#!/bin/bash
#
# Quick Test Script - AI Job Connector Agent
# Tests the mock version without any API keys
#

set -e  # Exit on error

echo "🚀 AI Job Connector Agent - Quick Test"
echo "======================================"
echo ""

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment not activated"
    echo "   Run: source .venv/bin/activate"
    echo ""
    exit 1
fi

echo "✓ Virtual environment activated"
echo ""

# Test 1: Unit tests
echo "📋 Test 1: Running unit tests..."
pytest tests/test_models.py -v --tb=short -q
echo "✅ Model tests passed!"
echo ""

# Test 2: Mock test suite
echo "📋 Test 2: Running mock test suite..."
python test_mock.py
echo ""

# Test 3: Mock CLI commands
echo "📋 Test 3: Testing mock CLI..."

# Demo
echo ""
echo "  → Running demo..."
job-connector-mock demo > /dev/null 2>&1
echo "  ✓ Demo completed"

# Single search
echo "  → Testing single search..."
job-connector-mock search -c "Anthropic" -t "AI Researcher" -o /tmp/test_single.json > /dev/null 2>&1
if [ -f /tmp/test_single.json ]; then
    echo "  ✓ Single search completed (output: /tmp/test_single.json)"
else
    echo "  ✗ Single search failed"
    exit 1
fi

# Batch processing
echo "  → Testing batch processing..."
cat > /tmp/test_batch.json << 'EOF'
[
  {"company_name": "OpenAI", "job_title": "Software Engineer"},
  {"company_name": "Tesla", "job_title": "Autopilot Engineer"}
]
EOF

job-connector-mock batch -f /tmp/test_batch.json -o /tmp/test_batch_results.json > /dev/null 2>&1

if [ -f /tmp/test_batch_results.json ]; then
    echo "  ✓ Batch processing completed (output: /tmp/test_batch_results.json)"

    # Validate JSON
    python -m json.tool /tmp/test_batch_results.json > /dev/null 2>&1
    echo "  ✓ Output JSON is valid"

    # Check results
    result_count=$(python -c "import json; data=json.load(open('/tmp/test_batch_results.json')); print(data['total_jobs'])")
    echo "  ✓ Processed $result_count jobs"
else
    echo "  ✗ Batch processing failed"
    exit 1
fi

echo ""
echo "✅ All CLI tests passed!"
echo ""

# Summary
echo "======================================"
echo "🎉 All Tests Passed!"
echo "======================================"
echo ""
echo "What was tested:"
echo "  ✓ 15 unit tests (models, config)"
echo "  ✓ Mock test suite (3 comprehensive tests)"
echo "  ✓ Demo command"
echo "  ✓ Single search command"
echo "  ✓ Batch processing command"
echo "  ✓ JSON export and validation"
echo ""
echo "Sample outputs created:"
echo "  - /tmp/test_single.json (single search result)"
echo "  - /tmp/test_batch_results.json (batch results)"
echo ""
echo "Next steps:"
echo "  • View results: cat /tmp/test_batch_results.json | jq '.'"
echo "  • Run demo: job-connector-mock demo"
echo "  • Read guide: cat TESTING_GUIDE.md"
echo ""
echo "✨ Ready to use without any API keys!"
