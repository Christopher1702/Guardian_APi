import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import React from 'react';
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

const meals = [
  {
    day: 'Monday',
    title: 'Grilled Chicken Bowl',
    image: 'https://your-link.com/chicken.jpg',
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

export default function MealPlan() {
  const router = useRouter();

  return (
    <LinearGradient
      colors={['#cbd5e1', '#94a3b8']}
      start={{ x: 0, y: 0 }}
      end={{ x: 0, y: 1 }}
      style={styles.gradient}
    >
      <SafeAreaView style={styles.container}>
        {/* Meal Cards */}
        <ScrollView contentContainerStyle={styles.scroll}>
          {meals.map((meal, index) => (
            <TouchableOpacity key={index} style={styles.card} onPress={() => router.push('/meal_build')}>
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

        {/* Bottom Island Bar */}
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
    paddingBottom: 140, // extra space for island bar
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




