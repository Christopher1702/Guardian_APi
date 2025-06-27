import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { useLocalSearchParams, useRouter } from 'expo-router';
import React, { useState } from 'react';
import {
  KeyboardAvoidingView,
  Platform,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import Animated, {
  FadeInDown,
  FadeOutUp,
} from 'react-native-reanimated';
import { BASE_URL } from '../constants/api';

export default function Mogi() {
  const router = useRouter();
  const { day } = useLocalSearchParams();

  const [showSubOptions, setShowSubOptions] = useState(false);
  const [showInput, setShowInput] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [messages, setMessages] = useState<string[]>([]);

  const handleSubPress = (category: string) => {
    if (['SFU', 'Gym', 'Home'].includes(category)) {
      setSelectedCategory(category);
      setShowInput(true);
    }
  };

  const handleSubmit = async () => {
    if (!inputValue.trim()) return;

    try {
      const content = `${day} - ${selectedCategory}: ${inputValue}`;
      await fetch(`${BASE_URL}/save_schedule`, {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain' },
        body: content,
      });

      setMessages(prev => [...prev, inputValue]);
      setInputValue('');
    } catch (error) {
      console.error('Error saving schedule:', error);
    }
  };

  const handleBackToCategories = () => {
    setShowInput(false);
    setInputValue('');
    setMessages([]);
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={{ flex: 1 }}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 0}
    >
      <LinearGradient
        colors={['#ffffff', '#e9d5ff']}
        start={{ x: 0, y: 0 }}
        end={{ x: 0, y: 1 }}
        style={{ flex: 1 }}
      >
        <View style={styles.container}>
          <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
            <Ionicons name="arrow-back" size={24} color="#14B8A6" />
          </TouchableOpacity>

          {showInput && (
            <TouchableOpacity style={styles.topRight} onPress={handleBackToCategories}>
              <Text style={styles.topRightText}>Back</Text>
            </TouchableOpacity>
          )}

          <Text style={styles.dayTitle}>{day}</Text>

          <View style={styles.buttonGroup}>
            {!showSubOptions && !showInput && (
              <>
                <TouchableOpacity
                  style={styles.optionButton}
                  onPress={() => setShowSubOptions(true)}
                >
                  <Text style={styles.optionText}>Every {day}</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.optionButton}>
                  <Text style={styles.optionText}>One time event</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.optionButton}>
                  <Text style={styles.optionText}>Custom</Text>
                </TouchableOpacity>
              </>
            )}

            {showSubOptions && !showInput && (
              <>
                <TouchableOpacity
                  style={[styles.subButton, { backgroundColor: '#ef4444' }]}
                  onPress={() => handleSubPress('SFU')}
                >
                  <Text style={styles.subButtonText}>SFU</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.subButton, { backgroundColor: '#3b82f6' }]}
                  onPress={() => handleSubPress('Gym')}
                >
                  <Text style={styles.subButtonText}>Gym</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.subButton, { backgroundColor: '#10b981' }]}
                  onPress={() => handleSubPress('Home')}
                >
                  <Text style={styles.subButtonText}>Home</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.subButton, { backgroundColor: '#9ca3af' }]}
                  onPress={() => handleSubPress('Other')}
                >
                  <Text style={styles.subButtonText}>Other</Text>
                </TouchableOpacity>
              </>
            )}
          </View>

          {showInput && (
            <Animated.View
              entering={FadeInDown.springify().mass(0.3)}
              exiting={FadeOutUp}
              style={styles.inputSection}
            >
              <View style={styles.promptBubble}>
                <Text style={styles.promptText}>
                  What would you like me to remember for {selectedCategory}?
                </Text>
              </View>

              {messages.map((msg, index) => (
                <View key={index} style={styles.userBubble}>
                  <Text style={styles.userText}>{msg}</Text>
                </View>
              ))}
            </Animated.View>
          )}

          {showInput && (
            <View style={styles.inputRow}>
              <View style={styles.inputContainer}>
                <TextInput
                  style={styles.inputBox}
                  placeholder="Type here..."
                  placeholderTextColor="#94a3b8"
                  value={inputValue}
                  onChangeText={setInputValue}
                />
                <TouchableOpacity onPress={handleSubmit} style={styles.iconInsideBox}>
                  <Ionicons name="arrow-forward" size={22} color="#14b8a6" />
                </TouchableOpacity>
              </View>
            </View>
          )}
        </View>
      </LinearGradient>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal: 24,
    paddingTop: 60,
    alignItems: 'center',
  },
  backButton: {
    position: 'absolute',
    top: 60,
    left: 24,
    zIndex: 10,
    backgroundColor: '#ffffff',
    padding: 8,
    borderRadius: 20,
    elevation: 4,
  },
  topRight: {
    position: 'absolute',
    top: 60,
    right: 24,
    padding: 8,
    zIndex: 10,
  },
  topRightText: {
    color: '#0f172a',
    fontWeight: '600',
  },
  dayTitle: {
    fontSize: 28,
    fontWeight: '700',
    color: '#1E293B',
    marginTop: 40,
    marginBottom: '30%',
  },
  buttonGroup: {
    width: '100%',
    alignItems: 'center',
    gap: '8%',
  },
  optionButton: {
    width: '50%',
    height: '15%',
    backgroundColor: '#ffffff',
    paddingVertical: 14,
    borderRadius: 16,
    alignItems: 'center',
    elevation: 8,
    marginBottom: 20,
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 6 },
        shadowOpacity: 0.2,
        shadowRadius: 10,
      },
    }),
  },
  optionText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#0f172a',
    marginVertical: '10%',
  },
  subButton: {
    width: '50%',
    height: '12%',
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
    elevation: 8,
    marginBottom: 20,
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 6 },
        shadowOpacity: 0.2,
        shadowRadius: 10,
      },
    }),
  },
  subButtonText: {
    fontSize: 16,
    fontWeight: '700',
    color: '#ffffff',
  },
  inputSection: {
    width: '100%',
    paddingHorizontal: 4,
    paddingBottom: 100,
  },
  promptBubble: {
    backgroundColor: '#ffffff',
    padding: 14,
    borderRadius: 18,
    alignSelf: 'flex-start',
    maxWidth: '80%',
    elevation: 6,
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 6 },
        shadowOpacity: 0.2,
        shadowRadius: 10,
      },
    }),
  },
  promptText: {
    fontSize: 15,
    color: '#0f172a',
  },
  userBubble: {
    backgroundColor: '#14b8a6',
    padding: 12,
    borderRadius: 18,
    alignSelf: 'flex-end',
    marginTop: 10,
    maxWidth: '80%',
  },
  userText: {
    fontSize: 15,
    color: '#ffffff',
  },
  inputRow: {
    position: 'absolute',
    bottom: 40,
    left: 16,
    right: 16,
    backgroundColor: '#f8fafc',
    borderRadius: 32,
    paddingHorizontal: 16,
    paddingVertical: 6,
    flexDirection: 'row',
    alignItems: 'center',
    elevation: 6,
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.1,
        shadowRadius: 6,
      },
    }),
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  inputBox: {
    flex: 1,
    fontSize: 16,
    paddingVertical: 8,
    color: '#1e293b',
  },
  iconInsideBox: {
    marginLeft: 8,
  },
});

