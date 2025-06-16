import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import React, { useState } from 'react';
import {
  Keyboard,
  KeyboardAvoidingView,
  Platform,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  TouchableWithoutFeedback,
  View,
} from 'react-native';
import { BASE_URL } from '../constants/api';

export default function MealBuild() {
  const [inputValue, setInputValue] = useState('');
  const [imageUri, setImageUri] = useState<string | null>(null);
  const router = useRouter();

  const handleSubmit = async () => {
    if (!inputValue) return;
    try {
      const response = await fetch(`${BASE_URL}/meal_build`, {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain' },
        body: inputValue,
      });
      const result = await response.text();
      console.log('Server response:', result);
      setInputValue('');
    } catch (error) {
      console.error('Gemini lost connection', error);
    }
  };

  return (
    <LinearGradient
      colors={['#cbd5e1', '#94a3b8']}
      start={{ x: 0, y: 0 }}
      end={{ x: 0, y: 1 }}
      style={{ flex: 1 }}
    >
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
          <View style={styles.container}>
            <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
              <Text style={styles.backText}>← Back</Text>
            </TouchableOpacity>

            <View style={[styles.promptBox, { backgroundColor: '#ffffff' }]}>  
              <Text style={[styles.prompt, { color: '#0F172A' }]}>Monday Meal Plan</Text>
            </View>

            <View style={styles.bottomContainer}>  
              <View style={[styles.inputRow, { backgroundColor: '#ffffff' }]}> 
                <TextInput
                  style={[styles.input, { color: '#1E293B' }]} 
                  placeholder="What do you feel hunrgy for?"
                  placeholderTextColor="#94A3B8"
                  value={inputValue}
                  onChangeText={setInputValue}
                />

                <TouchableOpacity onPress={handleSubmit} style={styles.arrowButton}>
                  <Text style={[styles.arrow, { color: '#14B8A6' }]}>➤</Text>
                </TouchableOpacity>
              </View>
            </View>

          </View>
        </TouchableWithoutFeedback>
      </KeyboardAvoidingView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal: 24,
    paddingTop: 60,
    justifyContent: 'flex-start',
  },
  backButton: {
    position: 'absolute',
    top: 60,
    left: 24,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 10,
    backgroundColor: '#ffffff',
    elevation: 4,
  },
  backText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#14B8A6',
  },
  promptBox: {
    alignItems: 'center',
    marginTop: '15%',
    padding: 16,
    borderRadius: 12,
    elevation: 6,
  },
  prompt: {
    fontSize: 18,
    fontWeight: '600',
    fontFamily: 'System',
    textAlign: 'center',
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    elevation: 5,
  },
  input: {
    flex: 1,
    fontSize: 16,
    fontFamily: 'Helvetica Neue',
    paddingRight: 10,
  },
  arrowButton: {
    padding: 8,
  },
  arrow: {
    fontSize: 20,
  },
  bottomContainer: {
    position: 'absolute',
    bottom: 50,
    left: 24,
    right: 24,
  },
});





