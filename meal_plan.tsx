import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import React, { useEffect, useState } from 'react';
import {
  ImageBackground,
  Platform,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { BASE_URL } from '../constants/api';

export default function MealPlan() {
  const router = useRouter();
  const [mondayImage, setMondayImage] = useState('https://your-link.com/chicken.jpg'); // fallback
  const [mondayTitle, setMondayTitle] = useState('Grilled Chicken Bowl');

  useEffect(() => {
    const fetchMondayData = async () => {
      try {
        const imageRes = await fetch(`${BASE_URL}/fetch_image`);
        const imageLink = await imageRes.text();
        if (imageLink) setMondayImage(imageLink);
      } catch (err) {
        console.error('Failed to load image:', err);
      }

      try {
        const recipeRes = await fetch(`${BASE_URL}/fetch_recipe`);
        const recipeText = await recipeRes.text();
        if (recipeText) {
          const trimmed = recipeText.split('\n')[0]; // Get first line as title
          setMondayTitle(trimmed.slice(0, 60)); // trim for UI
        }
      } catch (err) {
        console.error('Failed to load title:', err);
      }
    };

    fetchMondayData();
  }, []);

  const meals = [
    {
      day: 'Monday',
      title: mondayTitle,
      image: mondayImage,
    },
    {
      day: 'Tuesday',
      title: 'Veggie Skewers & Rice',
      image: 'https://your-link.com/skewers.jpg',
    },
    {
      day: 'Wednesday',
      title: 'Salmon Salad',
      image: 'https://your-link.com/salmon.jpg',
    },
    {
      day: 'Thursday',
      title: 'Pasta Primavera',
      image: 'https://your-link.com/pasta.jpg',
    },
    {
      day: 'Friday',
      title: 'Beef Stir‑Fry',
      image: 'https://your-link.com/beef.jpg',
    },
    {
      day: 'Saturday',
      title: 'Veggie Tacos',
      image: 'https://your-link.com/tacos.jpg',
    },
  ];

  return (
    <LinearGradient
      colors={['#cbd5e1', '#94a3b8']}
      start={{ x: 0, y: 0 }}
      end={{ x: 0, y: 1 }}
      style={styles.gradient}
    >
      <SafeAreaView style={styles.container}>
        <ScrollView contentContainerStyle={styles.scroll}>
          {meals.map((meal, index) => (
            <TouchableOpacity
              key={index}
              style={styles.card}
              onPress={() => router.push('/meal_build')}
            >
              <ImageBackground
                source={{ uri: meal.image }}
                style={styles.image}
                imageStyle={{ borderRadius: 20 }}
              >
                <View style={styles.label}>
                  <Text style={styles.dayText}>{meal.day}</Text>
                  <Text style={styles.titleText}>{meal.title}</Text>
                </View>
              </ImageBackground>
            </TouchableOpacity>
          ))}
        </ScrollView>

        <View style={styles.bottomIsland}>
          <TouchableOpacity onPress={() => router.push('/')}>
            <Ionicons name="home" size={24} color="#334155" />
          </TouchableOpacity>

          <TouchableOpacity>
            <Ionicons name="fast-food-outline" size={28} color="#14B8A6" />
          </TouchableOpacity>

          <TouchableOpacity onPress={() => router.push('/mogi')}>
            <Ionicons name="person-outline" size={24} color="#334155" />
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  gradient: {
    flex: 1,
  },
  container: {
    flex: 1,
  },
  scroll: {
    paddingTop: 60,
    paddingBottom: 140,
    paddingHorizontal: 24,
  },
  card: {
    marginBottom: 24,
    borderRadius: 20,
    overflow: 'hidden',
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 6 },
        shadowOpacity: 0.1,
        shadowRadius: 8,
      },
      android: {
        elevation: 5,
      },
    }),
  },
  image: {
    width: '100%',
    height: 180,
    justifyContent: 'flex-end',
  },
  label: {
    padding: 12,
    backgroundColor: 'rgba(0,0,0,0.4)',
    borderBottomLeftRadius: 20,
    borderBottomRightRadius: 20,
  },
  dayText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  titleText: {
    fontSize: 16,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  bottomIsland: {
    position: 'absolute',
    bottom: 20,
    left: 24,
    right: 24,
    height: 64,
    borderRadius: 32,
    backgroundColor: '#FFFFFF',
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 6 },
        shadowOpacity: 0.15,
        shadowRadius: 10,
      },
      android: {
        elevation: 8,
      },
    }),
  },
});




