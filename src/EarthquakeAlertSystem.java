import javax.swing.*;
import javax.swing.border.Border;
import javax.swing.border.EmptyBorder;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.Random;
import org.json.JSONObject;
import org.json.JSONArray;
/**
 * A real-time, interactive earthquake detection and alert system simulation
 * using Java Swing.
 * This version uses the system "Look and Feel" and a modern, web-like design
 * with CSS-like colors and a test event dropdown.
 *
 * @author Gemini
 * @version 1.4 (Modern Swing GUI)
 */
public class EarthquakeAlertSystem {

    // --- Configuration ---
    private static final double MIN_MAGNITUDE = 1.0;
    private static final double MAX_MAGNITUDE = 9.5;
    private static final int SIMULATION_INTERVAL_MS = 3000; // 3 seconds

    // Alert Thresholds
    private static final double DANGER_THRESHOLD = 6.0;
    private static final double WARNING_THRESHOLD = 4.0;

    // --- Modern Color Palette (Web-like) ---
    private static final Color COLOR_SAFE = new Color(0, 150, 136); // Teal
    private static final Color COLOR_WARNING = new Color(255, 152, 0); // Orange
    private static final Color COLOR_DANGER = new Color(211, 47, 47); // Red
    private static final Color COLOR_INIT = new Color(69, 90, 100); // Blue Grey
    private static final Color COLOR_PAUSED = new Color(117, 117, 117); // Grey
    private static final Color COLOR_LOG_BACKGROUND = new Color(245, 245, 245); // Very light grey
    private static final Color COLOR_PANEL_BACKGROUND = new Color(255, 255, 255); // White

    // --- GUI Components ---
    private JFrame mainFrame;
    private JTextArea logArea;
    private JPanel statusPanel; // Panel to change color
    private JLabel statusLabel; // Text label
    private JButton toggleButton;
    private JComboBox<String> testEventBox;

    // --- Simulation State ---
    private volatile boolean simulationRunning = true;
    private Thread sensorThread;
    private final Random random = new Random();
    private final String[] locations = { "Tokyo, Japan", "San Francisco, USA", "Jakarta, Indonesia",
            "Mexico City, Mexico", "Istanbul, Turkey" };

    /**
     * Main method to launch the application.
     */
    public static void main(String[] args) {
        // Set the "Look and Feel" to match the user's OS (Windows, macOS, etc.)
        // This makes the application look much more modern.
        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception e) {
            System.err.println("Warning: Could not set system Look and Feel.");
        }

        // Swing GUI operations must be run on the Event Dispatch Thread (EDT)
        SwingUtilities.invokeLater(() -> {
            EarthquakeAlertSystem app = new EarthquakeAlertSystem();
            app.createAndShowGUI();
        });
    }

    /**
     * Creates and configures the main GUI window and components.
     */
    private void createAndShowGUI() {
        // --- Set up the main window (JFrame) ---
        mainFrame = new JFrame("Real-Time Earthquake Alert System");
        mainFrame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        mainFrame.setSize(650, 450); // Increased size
        mainFrame.setLocationRelativeTo(null); // Center on screen
        mainFrame.setLayout(new BorderLayout(0, 0)); // No gaps

        // --- 1. Status Panel (Top) ---
        statusPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 20, 20)); // Added padding
        statusPanel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));

        statusLabel = new JLabel("STATUS: INITIALIZING...");
        statusLabel.setFont(new Font("SansSerif", Font.BOLD, 24));
        statusPanel.add(statusLabel);
        setAlertStatus("INITIALIZING", COLOR_INIT, Color.WHITE); // Initial state

        // --- 2. Log Panel (Center) ---
        logArea = new JTextArea();
        logArea.setEditable(false);
        logArea.setFont(new Font("Monospaced", Font.PLAIN, 14));
        logArea.setMargin(new Insets(10, 10, 10, 10)); // Internal padding
        logArea.setBackground(COLOR_LOG_BACKGROUND);
        logArea.setForeground(new Color(50, 50, 50));

        JScrollPane scrollPane = new JScrollPane(logArea);
        scrollPane.setBorder(BorderFactory.createMatteBorder(1, 0, 1, 0, new Color(224, 224, 224))); // Top/Bottom border
        scrollPane.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_ALWAYS);

        // --- 3. Control Panel (Bottom) ---
        JPanel controlPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 10, 10)); // Gaps
        controlPanel.setBackground(COLOR_PANEL_BACKGROUND);
        controlPanel.setBorder(new EmptyBorder(10, 10, 10, 10)); // Padding

        // Pause/Resume Button
        toggleButton = new JButton("Pause Simulation");
        styleButton(toggleButton, new Color(25, 118, 210)); // Blue
        toggleButton.addActionListener(e -> toggleSimulation());
        controlPanel.add(toggleButton);

        // Test Event Dropdown
        String[] testEvents = { "Trigger Test Event...", "Test Danger (7.2)", "Test Warning (4.5)", "Test Safe (1.5)" };
        testEventBox = new JComboBox<>(testEvents);
        testEventBox.setFont(new Font("SansSerif", Font.PLAIN, 14));
        testEventBox.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
        testEventBox.addActionListener(e -> triggerTestEvent());
        controlPanel.add(testEventBox);

        // Clear Log Button
        JButton clearLogButton = new JButton("Clear Log");
        styleButton(clearLogButton, new Color(117, 117, 117)); // Grey
        clearLogButton.addActionListener(e -> logArea.setText(""));
        controlPanel.add(clearLogButton);

        // --- Add components to the frame ---
        mainFrame.add(statusPanel, BorderLayout.NORTH);
        mainFrame.add(scrollPane, BorderLayout.CENTER);
        mainFrame.add(controlPanel, BorderLayout.SOUTH);

        // --- Make window visible and start simulation ---
        mainFrame.setVisible(true);
        log("GUI initialized. Starting sensor simulation thread...");
        startSimulationThread();
    }

    /**
     * Helper method to style buttons for a modern look.
     */
    private void styleButton(JButton button, Color backgroundColor) {
        button.setFont(new Font("SansSerif", Font.BOLD, 14));
        button.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
        button.setForeground(Color.WHITE);
        button.setBackground(backgroundColor);
        button.setBorder(new EmptyBorder(10, 15, 10, 15)); // Padding
        button.setFocusPainted(false); // Remove ugly focus ring
    }

    /**
     * Starts the background thread that simulates earthquake sensor data.
     */
    private void startSimulationThread() {
        Runnable sensorSimulationTask = () -> {
            try {
                processEarthquakeData(1.5, "System Boot"); // Initial safe reading
                while (!Thread.currentThread().isInterrupted()) {
                    if (simulationRunning) {
                        double magnitude = MIN_MAGNITUDE + (MAX_MAGNITUDE - MIN_MAGNITUDE) * random.nextDouble();
                        magnitude = Math.round(magnitude * 10.0) / 10.0;
                        String location = locations[random.nextInt(locations.length)];
                        processEarthquakeData(magnitude, location);
                    }
                    Thread.sleep(SIMULATION_INTERVAL_MS);
                }
            } catch (InterruptedException e) {
                // Safely log from background thread
                SwingUtilities.invokeLater(() -> log("Simulation thread interrupted and stopping."));
            }
        };
        sensorThread = new Thread(sensorSimulationTask, "SensorSimulatorThread");
        sensorThread.setDaemon(true);
        sensorThread.start();
    }

    /**
     * Toggles the simulation between running and paused.
     */
    private void toggleSimulation() {
        simulationRunning = !simulationRunning;
        if (simulationRunning) {
            toggleButton.setText("Pause Simulation");
            styleButton(toggleButton, new Color(25, 118, 210)); // Blue
            log("Simulation RESUMED.");
        } else {
            toggleButton.setText("Resume Simulation");
            styleButton(toggleButton, new Color(255, 152, 0)); // Orange
            log("Simulation PAUSED.");
            // Update GUI on the Event Dispatch Thread (EDT)
            SwingUtilities.invokeLater(() -> setAlertStatus("PAUSED", COLOR_PAUSED, Color.WHITE));
        }
    }

    /**
     * Triggers a manual test event based on the JComboBox selection.
     */
    private void triggerTestEvent() {
        int selectedIndex = testEventBox.getSelectedIndex();
        if (selectedIndex == 0)
            return; // Ignore "Trigger Test Event..."

        if (simulationRunning) {
            toggleSimulation(); // Pause simulation to show test event
            log("--- Manual Test Event Triggered ---");
        }

        switch (selectedIndex) {
            case 1: // Test Danger
                processEarthquakeData(7.2, "Manual Test Location");
                break;
            case 2: // Test Warning
                processEarthquakeData(4.5, "Manual Test Location");
                break;
            case 3: // Test Safe
                processEarthquakeData(1.5, "Manual Test Location");
                break;
        }
        testEventBox.setSelectedIndex(0); // Reset dropdown
    }

    /**
     * Processes the mocked earthquake data and updates the GUI.
     * This uses SwingUtilities.invokeLater to safely update GUI components
     * from the sensor thread.
     */
    private void processEarthquakeData(double magnitude, String location) {
        String baseMessage = String.format("[Sensor Reading] Magnitude %.1f at %s", magnitude, location);

        if (magnitude >= DANGER_THRESHOLD) {
            String finalMessage = baseMessage + " -> DANGER! Major Earthquake Detected!";
            SwingUtilities.invokeLater(() -> {
                setAlertStatus("DANGER", COLOR_DANGER, Color.WHITE);
                log(finalMessage);
            });
        } else if (magnitude >= WARNING_THRESHOLD) {
            String finalMessage = baseMessage + " -> WARNING! Moderate Earthquake Detected.";
            SwingUtilities.invokeLater(() -> {
                setAlertStatus("WARNING", COLOR_WARNING, Color.WHITE);
                log(finalMessage);
            });
        } else {
            String finalMessage = baseMessage + " -> SAFE. Minor tremor or normal activity.";
            SwingUtilities.invokeLater(() -> {
                setAlertStatus("SAFE", COLOR_SAFE, Color.WHITE);
                log(finalMessage);
            });
        }
    }

    /**
     * A thread-safe method to set the status label text and color.
     * This MUST be called from the Event Dispatch Thread.
     */
    private void setAlertStatus(String status, Color backgroundColor, Color foregroundColor) {
        statusLabel.setText("STATUS: " + status);
        statusLabel.setForeground(foregroundColor);
        statusPanel.setBackground(backgroundColor);
    }

    /**
     * A thread-safe method to append messages to the log area.
     */
    private void log(String message) {
        if (SwingUtilities.isEventDispatchThread()) {
            // Already on the right thread
            logArea.append(message + "\n");
            logArea.setCaretPosition(logArea.getDocument().getLength());
        } else {
            // If called from another thread, schedule it on the EDT
            SwingUtilities.invokeLater(() -> {
                logArea.append(message + "\n");
                logArea.setCaretPosition(logArea.getDocument().getLength());
            });
        }
    }
}