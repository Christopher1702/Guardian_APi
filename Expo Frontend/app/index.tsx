import { Feather } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import { StatusBar } from "expo-status-bar";
import React, { useEffect, useMemo, useRef, useState } from "react";
import {
  Animated,
  Keyboard,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { BASE_URL } from "../constant/api";

type ChatMsg = { text: string; fromUser: boolean };

export default function HomeScreen() {
  const insets = useSafeAreaInsets();

  // UI
  const [greeting, setGreeting] = useState<string>("");
  const [inputText, setInputText] = useState("");
  const [messages, setMessages] = useState<ChatMsg[]>([]);
  const [kbVisible, setKbVisible] = useState(false);

  // Delivery/status states
  const [analyzing, setAnalyzing] = useState(false);
  const [readStatus, setReadStatus] = useState(false);
  const pulse = useRef(new Animated.Value(0.3)).current;

  // Data
  const [proteinValue, setProteinValue] = useState<string>("—");
  const [fibreValue, setFibreValue] = useState<string>("—");
  const [calorieValue, setCalorieValue] = useState<string>("—");

  // Dynamic greeting
  const computeGreeting = () => {
    const h = new Date().getHours();
    if (h < 12) return "Good morning";
    if (h < 18) return "Good afternoon";
    return "Good evening";
  };

  useEffect(() => {
    setGreeting(computeGreeting());
    const id = setInterval(() => setGreeting(computeGreeting()), 5 * 60 * 1000);
    return () => clearInterval(id);
  }, []);

  // Keyboard visibility (to remove safe-area gap when open)
  useEffect(() => {
    const show = Keyboard.addListener(
      Platform.OS === "ios" ? "keyboardWillShow" : "keyboardDidShow",
      () => setKbVisible(true)
    );
    const hide = Keyboard.addListener(
      Platform.OS === "ios" ? "keyboardWillHide" : "keyboardDidHide",
      () => setKbVisible(false)
    );
    return () => {
      show.remove();
      hide.remove();
    };
  }, []);

  // Animate “Analyzing…” pulse while waiting
  useEffect(() => {
    let loop: Animated.CompositeAnimation | null = null;
    if (analyzing) {
      pulse.setValue(0.3);
      loop = Animated.loop(
        Animated.sequence([
          Animated.timing(pulse, { toValue: 1, duration: 650, useNativeDriver: true }),
          Animated.timing(pulse, { toValue: 0.3, duration: 650, useNativeDriver: true }),
        ])
      );
      loop.start();
    }
    return () => {
      if (loop) loop.stop();
    };
  }, [analyzing, pulse]);

  // ---------------- Fetchers ----------------
  const loadProtein = async () => {
    try {
      const res = await fetch(`${BASE_URL}/protein`);
      const ct = res.headers.get("content-type") || "";
      if (ct.includes("application/json")) {
        const j = await res.json();
        const v = j.protein ?? j.Protein ?? j.value ?? "";
        setProteinValue(String(v || "—"));
      } else {
        setProteinValue((await res.text()).trim() || "—");
      }
    } catch (e) {
      console.error("protein fetch failed", e);
      setProteinValue("—");
    }
  };

  const loadFibre = async () => {
    try {
      const res = await fetch(`${BASE_URL}/fibre`);
      const ct = res.headers.get("content-type") || "";
      if (ct.includes("application/json")) {
        const j = await res.json();
        const v = j.fibre ?? j.Fibre ?? j.value ?? "";
        setFibreValue(String(v || "—"));
      } else {
        setFibreValue((await res.text()).trim() || "—");
      }
    } catch (e) {
      console.error("fibre fetch failed", e);
      setFibreValue("—");
    }
  };

  const loadCalories = async () => {
    try {
      const res = await fetch(`${BASE_URL}/calories`);
      const ct = res.headers.get("content-type") || "";
      if (ct.includes("application/json")) {
        const j = await res.json();
        const v = j.calories ?? j.Calories ?? j.value ?? "";
        setCalorieValue(String(v || "—"));
      } else {
        setCalorieValue((await res.text()).trim() || "—");
      }
    } catch (e) {
      console.error("calories fetch failed", e);
      setCalorieValue("—");
    }
  };

  // Fetch most recent AI response from backend
  const loadAiResponse = async (): Promise<string> => {
    try {
      const res = await fetch(`${BASE_URL}/ai_response`);
      const ct = res.headers.get("content-type") || "";
      if (ct.includes("application/json")) {
        const j = await res.json();
        const v = j.ai ?? j.Ai_Response ?? j.value ?? "";
        return String(v || "");
      }
      return (await res.text()).trim();
    } catch (e) {
      console.error("ai_response fetch failed", e);
      return "";
    }
  };

  useEffect(() => {
    loadProtein();
    loadFibre();
    loadCalories();
  }, []);

  // ---------------- Send input (plain text) ----------------
  const sendUserInput = async (text: string) => {
    try {
      const res = await fetch(`${BASE_URL}/upload_food`, {
        method: "POST",
        headers: { "Content-Type": "text/plain" },
        body: text,
      });

      if (res.ok) {
        await Promise.all([loadProtein(), loadFibre(), loadCalories()]);

        // Fetch AI’s reply, then append it and flip the status to "Read"
        const ai = await loadAiResponse();
        if (ai) {
          setMessages((prev) => [...prev, { text: ai, fromUser: false }]);
        }
        setAnalyzing(false);
        setReadStatus(true);
      } else {
        setAnalyzing(false);
      }

      await res.json().catch(() => ({}));
    } catch (err) {
      setAnalyzing(false);
      console.error("Error sending input:", err);
    }
  };

  // ---------------- Calendar ----------------
  const days = useMemo(() => {
    const today = new Date();
    const out: { label: string; isToday: boolean; key: string }[] = [];
    for (let offset = -2; offset <= 4; offset++) {
      const d = new Date(today);
      d.setDate(today.getDate() + offset);
      out.push({
        label: String(d.getDate()),
        isToday: offset === 0,
        key: d.toISOString().slice(0, 10),
      });
    }
    return out;
  }, []);

  // Helper to know if the last message is from user
  const lastIsUser = messages.length > 0 && messages[messages.length - 1].fromUser;

  return (
    <View style={styles.root}>
      <StatusBar translucent backgroundColor="transparent" style="light" />

      {/* Header gradient */}
      <LinearGradient
        colors={["#8F7BFF", "#A18CFF", "#B8A8FF"]}
        start={{ x: 0.2, y: 0 }}
        end={{ x: 0.8, y: 1 }}
        style={[styles.header, { paddingTop: insets.top + 8 }]}
      >
        <View style={styles.headerTopRow}>
          <Text style={styles.headerTitle}>Home</Text>
          <View style={{ width: 28 }} />
        </View>

        {/* Calendar */}
        <View style={styles.calendarRow}>
          {days.map((d) => (
            <View key={d.key} style={[styles.dayPill, d.isToday && styles.dayPillActive]}>
              <Text style={[styles.dayPillText, d.isToday && styles.dayPillTextActive]}>
                {d.label}
              </Text>
            </View>
          ))}
        </View>

        {/* Calories */}
        <Text style={styles.kcalNumber}>{calorieValue}</Text>
        <Text style={styles.kcalSub}>Calorie</Text>

        {/* Dots */}
        <View style={styles.dotsRow}>
          {Array.from({ length: 40 }).map((_, i) => (
            <View key={i} style={[styles.dot, i % 6 === 0 && { opacity: 0.25 }]} />
          ))}
        </View>

        {/* Macros */}
        <View style={[styles.macroRow, { justifyContent: "center" }]}>
          <MacroItem label="Protein" value={proteinValue} />
          <MacroItem label="Fibre" value={fibreValue} />
        </View>
      </LinearGradient>

      {/* White section: messages + input bar anchored at bottom */}
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : "height"}
        style={{ flex: 1 }}
        keyboardVerticalOffset={0}
      >
        <View style={styles.content}>
          {/* Messages area (scrollable) */}
          <ScrollView
            style={styles.messagesScroll}
            contentContainerStyle={{ paddingHorizontal: 18, paddingTop: 10, paddingBottom: 12 }}
            keyboardShouldPersistTaps="handled"
          >
            <Text style={styles.headingText}>{greeting}</Text>

            {/* Bot bubble (static helper) */}
            <View style={styles.chatBubble}>
              <Text style={styles.chatBubbleText}>Would you like me to record your macros?</Text>
            </View>

            {/* Conversation bubbles */}
            {messages.map((msg, idx) => (
              <View
                key={`${idx}-${msg.fromUser ? "u" : "a"}`}
                style={[
                  styles.chatBubble,
                  msg.fromUser ? styles.userBubble : styles.botBubble, // left for AI
                ]}
              >
                <Text style={styles.chatBubbleText}>{msg.text}</Text>
              </View>
            ))}

            {/* Status text directly under the last user bubble */}
            {lastIsUser && (analyzing || readStatus) && (
              analyzing ? (
                <Animated.Text
                  style={[
                    styles.statusText,
                    { opacity: pulse, alignSelf: "flex-end" },
                  ]}
                >
                  Analyzing…
                </Animated.Text>
              ) : (
                <Text style={[styles.statusText, { alignSelf: "flex-end" }]}>Read</Text>
              )
            )}
          </ScrollView>

          {/* Fixed input bar */}
          <View
            style={[
              styles.inputWrapper,
              { marginBottom: kbVisible ? 7 : Math.max(insets.bottom, 8) },
            ]}
          >
            <Feather name="search" size={18} color="#6B7280" style={{ marginLeft: 12 }} />
            <TextInput
              style={styles.input}
              placeholder="Type meal here…"
              placeholderTextColor="#9CA3AF"
              value={inputText}
              onChangeText={setInputText}
              returnKeyType="done"
              onSubmitEditing={async () => {
                const trimmed = inputText.trim();
                if (trimmed.length) {
                  // user bubble
                  setMessages((prev) => [...prev, { text: trimmed, fromUser: true }]);
                  setInputText("");

                  // delivery status
                  setReadStatus(false);
                  setAnalyzing(true);

                  // send & then append AI bubble + mark Read
                  await sendUserInput(trimmed);
                }
              }}
            />
          </View>
        </View>
      </KeyboardAvoidingView>
    </View>
  );
}

/* Macro item */
const MacroItem = ({ label, value }: { label: string; value: string }) => (
  <View style={{ alignItems: "center", marginHorizontal: 20 }}>
    <Text style={styles.macroValue}>{value}</Text>
    <Text style={styles.macroLabel}>{label}</Text>
  </View>
);

const RADIUS = 20;
const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#F7F7FB" },

  header: {
    paddingHorizontal: 18,
    paddingBottom: 22,
    borderBottomLeftRadius: 28,
    borderBottomRightRadius: 28,
    overflow: "hidden",
  },
  headerTopRow: { flexDirection: "row", alignItems: "center", justifyContent: "space-between" },
  headerTitle: { color: "#fff", fontSize: 18, fontWeight: "600" },

  calendarRow: { flexDirection: "row", marginTop: 12, gap: 8, justifyContent: "space-between" },
  dayPill: {
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 12,
    backgroundColor: "rgba(255,255,255,0.18)",
  },
  dayPillActive: { backgroundColor: "#fff" },
  dayPillText: { color: "rgba(255,255,255,0.85)", fontSize: 12, fontWeight: "600" },
  dayPillTextActive: { color: "#5E53FF" },

  kcalNumber: { marginTop: 12, color: "#fff", fontSize: 72, fontWeight: "800", letterSpacing: 1, textAlign: "center" },
  kcalSub: { color: "rgba(255,255,255,0.9)", textAlign: "center", marginTop: -4, fontWeight: "600" },

  dotsRow: { marginTop: 8, flexDirection: "row", flexWrap: "wrap", justifyContent: "center", gap: 4 },
  dot: { width: 3, height: 3, borderRadius: 2, backgroundColor: "rgba(255,255,255,0.6)" },

  macroRow: {
    marginTop: 16,
    backgroundColor: "rgba(255,255,255,0.22)",
    borderRadius: RADIUS,
    flexDirection: "row",
    paddingVertical: 12,
    paddingHorizontal: 14,
  },
  macroValue: { color: "#fff", fontWeight: "800", fontSize: 16 },
  macroLabel: { color: "rgba(255,255,255,0.9)", fontSize: 12, marginTop: 2 },

  /* White section layout */
  content: { flex: 1, backgroundColor: "#F7F7FB" },
  messagesScroll: { flex: 1 },

  // Centered, soft heading
  headingText: {
    fontSize: 28,
    fontWeight: "300",
    textAlign: "center",
    color: "#111827",
    marginBottom: 8,
  },

  // Bot chat bubble
  chatBubble: {
    alignSelf: "flex-start",
    backgroundColor: "#fff",
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 16,
    borderTopLeftRadius: 4,
    shadowColor: "#000",
    shadowOpacity: 0.06,
    shadowOffset: { width: 0, height: 4 },
    shadowRadius: 10,
    elevation: 1,
    marginTop: 20,
    maxWidth: "80%",
  },
  chatBubbleText: { color: "#111827", fontSize: 14, fontWeight: "400" },

  // User bubble (right side)
  userBubble: {
    alignSelf: "flex-end",
    backgroundColor: "#DCF8C6",
    borderTopLeftRadius: 16,
    borderTopRightRadius: 4,
  },
  botBubble: { alignSelf: "flex-start" },

  // Delivery status text (Analyzing… / Read)
  statusText: {
    fontSize: 12,
    color: "#9CA3AF",
    marginTop: 4,
    marginBottom: 4,
  },

  // Fixed input bar
  inputWrapper: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#FFFFFF",
    borderRadius: 16,
    height: 52,
    shadowColor: "#000",
    shadowOpacity: 0.06,
    shadowOffset: { width: 0, height: 4 },
    shadowRadius: 12,
    elevation: 2,
    paddingRight: 12,
    marginHorizontal: 18,
  },
  input: {
    flex: 1,
    height: "100%",
    paddingHorizontal: 12,
    fontSize: 16,
    color: "#111827",
  },
});
