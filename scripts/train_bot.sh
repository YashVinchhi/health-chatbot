#!/bin/bash

# Train the Rasa model
echo "Training Rasa model..."
cd rasa_bot
rasa train

echo "Training completed. Model saved in models/ directory."