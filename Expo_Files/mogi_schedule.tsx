import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { useLocalSearchParams, useRouter } from 'expo-router';
import React, { useEffect, useState } from 'react';
import {
  KeyboardAvoidingView,
  Platform,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import Animated, { FadeIn, FadeInDown } from 'react-native-reanimated';

export default function Mogi() {
  const router = useRouter();
  const { day } = useLocalSearchParams();

  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedFrequency, setSelectedFrequency] = useState('');
  const [chatText, setChatText] = useState('');
  const [inputPrompt, setInputPrompt] = useState('');
  const [showFirstButtons, setShowFirstButtons] = useState(false);
  const [showSecondButtons, setShowSecondButtons] = useState(false);
  const [inputMode, setInputMode] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [messages, setMessages] = useState<string[]>([]);

  // Initial message animation
  useEffect(() => {
    const message = 'Based on the category I have set for you, which should we add to?';
    let current = '';
    let i = 0;

    const typeNext = () => {
      if (i < message.length) {
        current += message[i];
        setChatText(current);
        i++;
        setTimeout(typeNext, 5);
      } else {
        setShowFirstButtons(true);
      }
    };

    typeNext();
  }, []);

  // Follow-up message animation
  useEffect(() => {
    if (selectedCategory && chatText === '') {
      const message = `How often is this ${selectedCategory} event in your schedule?`;
      let current = '';
      let i = 0;

      const typeNext = () => {
        if (i < message.length) {
          current += message[i];
          setChatText(current);
          i++;
          setTimeout(typeNext, 5);
        } else {
          setShowSecondButtons(true);
        }
      };

      typeNext();
    }
  }, [selectedCategory, chatText]);

  // Typing animation for input prompt
  useEffect(() => {
    if (inputMode && inputPrompt === '') {
      const message = `What would you like me to remember for ${selectedCategory}?`;
      let current = '';
      let i = 0;

      const typeNext = () => {
        if (i < message.length) {
          current += message[i];
          setInputPrompt(current);
          i++;
          setTimeout(typeNext, 5);
        }
      };

      typeNext();
    }
  }, [inputMode, selectedCategory]);

  const handleCategorySelect = (category: string) => {
    setSelectedCategory(category);
    setShowFirstButtons(false);
    setChatText('');
  };

  const handleFrequencySelect = (frequency: string) => {
    setSelectedFrequency(frequency);
    setShowSecondButtons(false);
    setChatText('');
    setInputMode(true);
  };

  const sendPayload = () => {
    const payload = {
      day,
      category: selectedCategory,
      frequency: selectedFrequency,
      message: inputValue.trim(),
    };

    console.log('Sending payload:', payload);

    // Example: you can send to server here
    // fetch('/api/save', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify(payload),
    // });
  };

  const handleSubmit = () => {
    const trimmed = inputValue.trim();
    if (!trimmed) return;

    setMessages([...messages, trimmed]);
    sendPayload();
    setInputValue('');
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={{ flex: 1 }}
    >
      <LinearGradient
        colors={['#ffffff', '#e0f7ff']}
        start={{ x: 0, y: 0 }}
        end={{ x: 0, y: 1 }}
        style={{ flex: 1 }}
      >
        <View style={styles.container}>
          <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
            <Ionicons name="arrow-back" size={24} color="#14B8A6" />
          </TouchableOpacity>

          <Text style={styles.dayTitle}>{day}</Text>

          {!inputMode && (
            <View style={styles.chatBubble}>
              <Text style={styles.chatText}>{chatText}</Text>
            </View>
          )}

          {showFirstButtons && (
            <Animated.View entering={FadeIn.duration(300)} style={styles.centeredButtons}>
              <TouchableOpacity
                style={[styles.optionButton, { backgroundColor: '#ef4444' }]}
                onPress={() => handleCategorySelect('SFU')}
              >
                <Text style={styles.optionText}>SFU</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.optionButton, { backgroundColor: '#3b82f6' }]}
                onPress={() => handleCategorySelect('Gym')}
              >
                <Text style={styles.optionText}>Gym</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.optionButton, { backgroundColor: '#10b981' }]}
                onPress={() => handleCategorySelect('Home')}
              >
                <Text style={styles.optionText}>Home</Text>
              </TouchableOpacity>
            </Animated.View>
          )}

          {showSecondButtons && !inputMode && (
            <Animated.View entering={FadeIn.duration(300)} style={styles.centeredButtons}>
              <TouchableOpacity
                style={styles.white3DButton}
                onPress={() => handleFrequencySelect('Every')}
              >
                <Text style={styles.white3DButtonText}>Every {day}</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.white3DButton}
                onPress={() => handleFrequencySelect('One time only')}
              >
                <Text style={styles.white3DButtonText}>One time only</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.white3DButton}
                onPress={() => handleFrequencySelect('Custom')}
              >
                <Text style={styles.white3DButtonText}>Custom</Text>
              </TouchableOpacity>
            </Animated.View>
          )}

          {inputMode && (
            <Animated.View
              entering={FadeInDown.springify().mass(0.3)}
              style={styles.inputSection}
            >
              <View style={styles.promptBubble}>
                <Text style={styles.promptText}>{inputPrompt}</Text>
              </View>

              {messages.map((msg, index) => (
                <View key={index} style={styles.userBubble}>
                  <Text style={styles.userText}>{msg}</Text>
                </View>
              ))}
            </Animated.View>
          )}

          {inputMode && (
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
  dayTitle: {
    fontSize: 28,
    fontWeight: '700',
    color: '#1E293B',
    marginTop: 40,
    marginBottom: 16,
    alignSelf: 'center',
  },
  chatBubble: {
    backgroundColor: '#ffffff',
    padding: 14,
    borderRadius: 18,
    maxWidth: '90%',
    elevation: 6,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3,
    shadowRadius: 10,
    alignSelf: 'flex-start',
    marginTop: 50,
    minHeight: 60,
    justifyContent: 'center',
  },
  chatText: {
    fontSize: 15,
    color: '#0f172a',
  },
  centeredButtons: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: -100,
  },
  optionButton: {
    width: '60%',
    height: '13%',
    paddingVertical: 12,
    borderRadius: 16,
    alignItems: 'center',
    elevation: 5,
    marginBottom: 20,
  },
  optionText: {
    color: '#ffffff',
    fontWeight: '700',
    fontSize: 17,
    marginVertical: '10%',
  },
  white3DButton: {
    width: '60%',
    height: '13%',
    paddingVertical: 12,
    borderRadius: 16,
    backgroundColor: '#ffffff',
    alignItems: 'center',
    justifyContent: 'center',
    elevation: 6,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 6,
    marginBottom: 20,
  },
  white3DButtonText: {
    color: '#1E293B',
    fontWeight: '700',
    fontSize: 17,
  },
  inputSection: {
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
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.2,
    shadowRadius: 10,
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

