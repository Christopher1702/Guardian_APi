import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import React, { useEffect, useState } from 'react';
import {
  Image,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { BASE_URL } from '../constants/api';

export default function MealBuild() {
  const router = useRouter();
  const [recipeText, setRecipeText] = useState('');
  const [imageUrl, setImageUrl] = useState<string | null>(null);

  const fetchRecipeAndImage = async () => {
    try {
      const recipeRes = await fetch(`${BASE_URL}/fetch_recipe`);
      const recipe = await recipeRes.text();
      setRecipeText(recipe);

      const imageRes = await fetch(`${BASE_URL}/meal_img_link`);
      const imageLink = await imageRes.text();
      setImageUrl(imageLink || null);
    } catch (error) {
      console.error('Error fetching recipe or image:', error);
      setRecipeText('Error loading recipe.');
      setImageUrl(null);
    }
  };

  useEffect(() => {
    fetchRecipeAndImage();
  }, []);

  const handleHighProtein = async () => {
    try {
      await fetch(`${BASE_URL}/meal_build`, {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain' },
        body: 'Find a high-protein meal recipe.',
      });
      fetchRecipeAndImage();
    } catch (error) {
      console.error('High Protein request failed:', error);
    }
  };

  const handleCalorieDeficit = async () => {
    try {
      await fetch(`${BASE_URL}/meal_build`, {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain' },
        body: 'Find a low-calorie meal recipe for a calorie deficit.',
      });
      fetchRecipeAndImage();
    } catch (error) {
      console.error('Calorie Deficit request failed:', error);
    }
  };

  return (
    <LinearGradient
      colors={['#cbd5e1', '#94a3b8']}
      start={{ x: 0, y: 0 }}
      end={{ x: 0, y: 1 }}
      style={{ flex: 1 }}
    >
      <ScrollView contentContainerStyle={styles.container}>
        <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>

        <View style={[styles.promptBox, { backgroundColor: '#ffffff' }]}>
          <Text style={[styles.prompt, { color: '#0F172A' }]}>Monday Meal Plan</Text>
        </View>

        <View style={styles.buttonRow}>
          <TouchableOpacity style={styles.optionButton} onPress={handleHighProtein}>
            <Ionicons name="barbell-outline" size={20} color="#14B8A6" />
            <Text style={styles.optionText}>High Protein</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.optionButton} onPress={handleCalorieDeficit}>
            <Ionicons name="flame-outline" size={20} color="#14B8A6" />
            <Text style={styles.optionText}>Calorie Deficit</Text>
          </TouchableOpacity>
        </View>

        {recipeText !== '' && (
          <View style={styles.recipeContainer}>
            {imageUrl && (
              <Image source={{ uri: imageUrl }} style={styles.recipeImage} />
            )}
            <Text style={styles.recipeText}>{recipeText}</Text>
          </View>
        )}
      </ScrollView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: 24,
    paddingTop: 60,
    paddingBottom: 80,
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
    zIndex: 10,
  },
  backText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#14B8A6',
  },
  promptBox: {
    alignItems: 'center',
    marginTop: '20%',
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
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 30,
    gap: 16,
  },
  optionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#ffffff',
    borderRadius: 20,
    paddingVertical: 14,
    paddingHorizontal: 16,
    flex: 1,
    elevation: 5,
  },
  optionText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1E293B',
    marginLeft: 8,
  },
  recipeContainer: {
    marginTop: 30,
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 16,
    elevation: 4,
  },
  recipeImage: {
    width: '100%',
    height: 180,
    borderRadius: 12,
    marginBottom: 12,
  },
  recipeText: {
    fontSize: 14,
    color: '#334155',
    lineHeight: 20,
  },
});
