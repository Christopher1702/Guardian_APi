import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import React, { useEffect, useState } from 'react';
import {
  Platform,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';

export default function Home() {
  const [schedule, setSchedule] = useState('');
  const [day, setDay] = useState('');
  const router = useRouter();

  useEffect(() => {
    const currentDay = new Date().toLocaleDateString('en-US', { weekday: 'long' });
    setDay(currentDay);

    const fetchSchedule = async () => {
      try {
        const response = await fetch('https://guardian-api-3uje.onrender.com/agenda', {
          method: 'POST',
          headers: { 'Content-Type': 'text/plain' },
          body: currentDay,
        });
        const result = await response.text();
        setSchedule(result);
      } catch (error) {
        console.error('Error fetching schedule:', error);
        setSchedule('Unable to load schedule.');
      }
    };

    fetchSchedule();
  }, []);

  return (
    <LinearGradient
      colors={['#cbd5e1', '#94a3b8']}
      start={{ x: 0, y: 0 }}
      end={{ x: 0, y: 1 }}
      style={styles.gradient}
    >
      <SafeAreaView style={styles.container}>
        <ScrollView contentContainerStyle={styles.scrollContent}>
          <View style={styles.headerContainer}>
            <Text style={styles.greeting}>Good Morning</Text>
            <Text style={styles.name}>Christopher</Text>
          </View>

          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Agenda</Text>
          </View>

          <View style={styles.card}>
            <Text style={styles.cityRoute}>{day}</Text>
            <View style={styles.detailsRow}>
              {schedule.split('\n').map((line, idx) => (
                <Text key={idx} style={styles.detail}>{line}</Text>
              ))}
            </View>
          </View>

          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Meal Plan</Text>
          </View>
        </ScrollView>

        <View style={styles.bottomIsland}>
          <TouchableOpacity>
            <Ionicons name="home" size={24} color="#14B8A6" />
          </TouchableOpacity>

          <TouchableOpacity onPress={() => router.push('/meal_plan')}>
            <Ionicons name="fast-food-outline" size={24} color="#334155" />
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
  scrollContent: {
    paddingTop: 60,
    paddingHorizontal: 24,
    paddingBottom: 140,
  },
  headerContainer: {
    marginBottom: 10,
    paddingBottom: 20,
    top: -10,
  },
  greeting: {
    fontSize: 12,
    color: '#334155',
  },
  name: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1E293B',
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 14,
  },
  sectionTitle: {
    fontSize: 24,
    fontWeight: '600',
    color: '#0F172A',
  },
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 16,
    marginBottom: 40,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.05,
    shadowRadius: 6,
  },
  cityRoute: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1E293B',
    marginBottom: 10,
  },
  detailsRow: {
    flexDirection: 'column',
    gap: 6,
  },
  detail: {
    fontSize: 13,
    color: '#475569',
  },
  bottomIsland: {
    position: 'absolute',
    bottom: 20,
    left: 24,
    right: 24,
    height: 64,
    borderRadius: 32,
    backgroundColor: '#ffffff',
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


































