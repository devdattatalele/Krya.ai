#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use std::sync::{Arc, Mutex};
use tauri::{
    CustomMenuItem, Manager, SystemTray, SystemTrayEvent, SystemTrayMenu, SystemTrayMenuItem,
    Window, WindowEvent,
};
use tauri::GlobalShortcutManager;
use std::process::Command;
use reqwest;

// State to track if the API server is running
struct AppState {
    api_server_running: Arc<Mutex<bool>>,
    api_server_process: Arc<Mutex<Option<std::process::Child>>>,
}

// Clone implementation for AppState
impl Clone for AppState {
    fn clone(&self) -> Self {
        AppState {
            api_server_running: self.api_server_running.clone(),
            api_server_process: self.api_server_process.clone(),
        }
    }
}

// Function to toggle the spotlight window
fn toggle_spotlight_window(window: &Window) {
    if window.is_visible().unwrap() {
        window.hide().unwrap();
    } else {
        window.show().unwrap();
        window.set_focus().unwrap();
        
        // Position window at the top center (1/4 position)
        let monitor = window.current_monitor().unwrap().unwrap();
        let monitor_size = monitor.size();
        let window_size = window.inner_size().unwrap();
        
        let x = (monitor_size.width as i32 - window_size.width as i32) / 2;
        let y = monitor_size.height as i32 / 4 - window_size.height as i32 / 2;
        
        window.set_position(tauri::Position::Physical(tauri::PhysicalPosition { x, y })).unwrap();
    }
}

// Function to create the settings window
fn open_settings_window(app_handle: &tauri::AppHandle) {
    // Check if settings window already exists
    if let Some(settings_window) = app_handle.get_window("settings") {
        settings_window.show().unwrap();
        settings_window.set_focus().unwrap();
        return;
    }

    // Create settings window
    let settings_window = tauri::WindowBuilder::new(
        app_handle,
        "settings",
        tauri::WindowUrl::App("index.html".into()),
    )
    .title("Krya.ai Settings")
    .inner_size(600.0, 500.0)
    .resizable(true)
    .decorations(true)
    .center()
    .build()
    .expect("Failed to create settings window");

    // Set always on top
    settings_window.set_always_on_top(true).unwrap();
    
    // Set window to be shown
    settings_window.show().unwrap();
    settings_window.set_focus().unwrap();
}

// Function to open console window
fn open_console_window(app_handle: &tauri::AppHandle) {
    // Check if console window already exists
    if let Some(console_window) = app_handle.get_window("console") {
        console_window.show().unwrap();
        console_window.set_focus().unwrap();
        return;
    }

    // Create console window
    let console_window = tauri::WindowBuilder::new(
        app_handle,
        "console",
        tauri::WindowUrl::App("index.html".into()),
    )
    .title("Krya.ai Console")
    .inner_size(700.0, 500.0)
    .resizable(true)
    .decorations(true)
    .center()
    .build()
    .expect("Failed to create console window");

    console_window.show().unwrap();
    console_window.set_focus().unwrap();
}

// Function to start the API server
fn start_api_server(app_state: &tauri::State<AppState>) -> Result<(), String> {
    let mut api_server_running = app_state.api_server_running.lock().unwrap();
    let mut api_server_process = app_state.api_server_process.lock().unwrap();
    
    if *api_server_running {
        return Ok(());
    }
    
    // Try to find the resource directory using current_exe
    let exe_path = std::env::current_exe().map_err(|e| format!("Failed to get current executable path: {}", e))?;
    let exe_dir = exe_path.parent().ok_or_else(|| "Failed to get executable directory".to_string())?;
    
    // Try different possible resource paths
    let possible_resource_paths = vec![
        exe_dir.join("resources").join("src"),
        exe_dir.join("..").join("Resources").join("resources").join("src"),  // macOS bundle
    ];
    
    let mut resource_path = None;
    for path in possible_resource_paths {
        if path.exists() {
            resource_path = Some(path);
            break;
        }
    }
    
    println!("Checking for resource directory...");
    
    // Check if the resource path exists
    if resource_path.is_none() {
        // Fall back to development paths
        println!("Resource directory not found, falling back to development paths");
        
        // For development, use relative path
        let mut server_path = std::env::current_dir()
            .map_err(|e| format!("Failed to get current directory: {}", e))?;
        
        println!("Current directory: {:?}", server_path);
        
        // Move up from src-tauri directory to ui
        server_path.pop();
        
        // Move up from ui directory to the project root
        server_path.pop();
        
        println!("Project root directory: {:?}", server_path);
        
        // Add path to Python server
        let mut python_server_path = server_path.clone();
        python_server_path.push("src");
        python_server_path.push("run_server.py");
        
        println!("Starting Python server at: {:?}", python_server_path);
        
        // Check if the file exists
        if !python_server_path.exists() {
            return Err(format!("Python server script not found at: {:?}", python_server_path));
        }
        
        // Determine Python command based on platform
        let python_cmd = if cfg!(target_os = "windows") {
            "python"
        } else {
            "python3"
        };
        
        // Start the API server in a separate process
        let child = Command::new(python_cmd)
            .arg(&python_server_path)
            .arg("--port")
            .arg("8000")
            .current_dir(server_path.join("src"))
            .spawn();
        
        match child {
            Ok(process) => {
                println!("Python API server started with PID: {}", process.id());
                *api_server_process = Some(process);
                *api_server_running = true;
                
                // Give the server more time to start (increased from 2 to 5 seconds)
                std::thread::sleep(std::time::Duration::from_secs(5));
                
                // Try to ping the server to make sure it's running
                let status_check = std::thread::spawn(|| {
                    // Try several times to connect to the server
                    for _ in 0..5 {
                        std::thread::sleep(std::time::Duration::from_secs(1));
                        match reqwest::blocking::get("http://localhost:8000/") {
                            Ok(response) => {
                                if response.status().is_success() {
                                    println!("API server is responding correctly");
                                    return true;
                                }
                            },
                            Err(_) => {}
                        }
                    }
                    println!("API server is not responding after multiple attempts");
                    false
                });
                
                // Wait for the status check to complete
                match status_check.join() {
                    Ok(true) => println!("API server connection verified"),
                    _ => println!("Could not verify API server connection, but continuing anyway"),
                }
                
                Ok(())
            },
            Err(e) => {
                eprintln!("Failed to start Python API server: {}", e);
                Err(format!("Failed to start API server: {}", e))
            }
        }
    } else {
        // Production mode - use bundled resources
        let resource_path = resource_path.unwrap();
        let run_server_path = resource_path.join("run_server.py");
        println!("Starting Python server from bundled resources at: {:?}", run_server_path);
        
        // Determine Python command based on platform
        let python_cmd = if cfg!(target_os = "windows") {
            "python"
        } else {
            "python3"
        };
        
        // Start the API server in a separate process
        let child = Command::new(python_cmd)
            .arg(&run_server_path)
            .arg("--port")
            .arg("8000")
            .current_dir(&resource_path)
            .spawn();
        
        match child {
            Ok(process) => {
                println!("Python API server started with PID: {}", process.id());
                *api_server_process = Some(process);
                *api_server_running = true;
                
                // Give the server more time to start (increased from 2 to 5 seconds)
                std::thread::sleep(std::time::Duration::from_secs(5));
                
                // Try to ping the server to make sure it's running
                let status_check = std::thread::spawn(|| {
                    // Try several times to connect to the server
                    for _ in 0..5 {
                        std::thread::sleep(std::time::Duration::from_secs(1));
                        match reqwest::blocking::get("http://localhost:8000/") {
                            Ok(response) => {
                                if response.status().is_success() {
                                    println!("API server is responding correctly");
                                    return true;
                                }
                            },
                            Err(_) => {}
                        }
                    }
                    println!("API server is not responding after multiple attempts");
                    false
                });
                
                // Wait for the status check to complete
                match status_check.join() {
                    Ok(true) => println!("API server connection verified"),
                    _ => println!("Could not verify API server connection, but continuing anyway"),
                }
                
                Ok(())
            },
            Err(e) => {
                eprintln!("Failed to start Python API server: {}", e);
                
                // Try alternative Python command if first attempt failed
                if python_cmd == "python3" {
                    println!("Trying with 'python' instead...");
                    let child = Command::new("python")
                        .arg(&run_server_path)
                        .arg("--port")
                        .arg("8000")
                        .current_dir(&resource_path)
                        .spawn();
                    
                    match child {
                        Ok(process) => {
                            println!("Python API server started with PID: {}", process.id());
                            *api_server_process = Some(process);
                            *api_server_running = true;
                            
                            // Give the server more time to start (increased from 2 to 5 seconds)
                            std::thread::sleep(std::time::Duration::from_secs(5));
                            
                            // Try to ping the server to make sure it's running
                            let status_check = std::thread::spawn(|| {
                                // Try several times to connect to the server
                                for _ in 0..5 {
                                    std::thread::sleep(std::time::Duration::from_secs(1));
                                    match reqwest::blocking::get("http://localhost:8000/") {
                                        Ok(response) => {
                                            if response.status().is_success() {
                                                println!("API server is responding correctly");
                                                return true;
                                            }
                                        },
                                        Err(_) => {}
                                    }
                                }
                                println!("API server is not responding after multiple attempts");
                                false
                            });
                            
                            // Wait for the status check to complete
                            match status_check.join() {
                                Ok(true) => println!("API server connection verified"),
                                _ => println!("Could not verify API server connection, but continuing anyway"),
                            }
                            
                            return Ok(());
                        },
                        Err(e2) => {
                            eprintln!("Failed to start with alternative Python command: {}", e2);
                            return Err(format!("Failed to start API server with both python3 and python: {} / {}", e, e2));
                        }
                    }
                }
                
                Err(format!("Failed to start API server: {}", e))
            }
        }
    }
}

// Function to stop the API server
fn stop_api_server(app_state: &AppState) {
    let mut api_server_running = app_state.api_server_running.lock().unwrap();
    let mut api_server_process = app_state.api_server_process.lock().unwrap();
    
    if let Some(mut process) = api_server_process.take() {
        println!("Stopping Python API server");
        #[cfg(target_os = "windows")]
        {
            // On Windows, we need to use taskkill to kill the process tree
            let _ = Command::new("taskkill")
                .args(&["/F", "/T", "/PID", &process.id().to_string()])
                .output();
        }
        #[cfg(not(target_os = "windows"))]
        {
            // On Unix-like systems, we can kill the process directly
            let _ = process.kill();
        }
        
        *api_server_running = false;
    }
}

// Command to open settings window
#[tauri::command]
fn open_settings(app_handle: tauri::AppHandle) {
    open_settings_window(&app_handle);
}

// Command to open console window
#[tauri::command]
fn open_console(app_handle: tauri::AppHandle) {
    open_console_window(&app_handle);
}

// Command to quit the application
#[tauri::command]
fn quit_app(app_handle: tauri::AppHandle, app_state: tauri::State<AppState>) {
    // Stop the API server before quitting
    stop_api_server(&app_state);
    app_handle.exit(0);
}

fn main() {
    // Create system tray menu
    let quit = CustomMenuItem::new("quit".to_string(), "Quit");
    let show = CustomMenuItem::new("show".to_string(), "Show");
    let settings = CustomMenuItem::new("settings".to_string(), "Settings");
    let console = CustomMenuItem::new("console".to_string(), "Console");
    
    let tray_menu = SystemTrayMenu::new()
        .add_item(show)
        .add_item(settings)
        .add_item(console)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(quit);
    
    let system_tray = SystemTray::new().with_menu(tray_menu);

    // Initialize app state
    let app_state = AppState {
        api_server_running: Arc::new(Mutex::new(false)),
        api_server_process: Arc::new(Mutex::new(None)),
    };
    
    tauri::Builder::default()
        .manage(app_state.clone())
        .invoke_handler(tauri::generate_handler![open_settings, open_console, quit_app])
        .system_tray(system_tray)
        .on_system_tray_event(|app, event| match event {
            SystemTrayEvent::MenuItemClick { id, .. } => match id.as_str() {
                "quit" => {
                    // Stop the API server before quitting
                    let app_state = app.state::<AppState>();
                    stop_api_server(&app_state);
                    app.exit(0);
                }
                "show" => {
                    let window = app.get_window("main").unwrap();
                    toggle_spotlight_window(&window);
                }
                "settings" => {
                    open_settings_window(app);
                }
                "console" => {
                    open_console_window(app);
                }
                _ => {}
            },
            SystemTrayEvent::LeftClick { .. } => {
                let window = app.get_window("main").unwrap();
                toggle_spotlight_window(&window);
            }
            _ => {}
        })
        .on_window_event(|event| {
            if let WindowEvent::Focused(false) = event.event() {
                // Auto-hide the main window when it loses focus (spotlight behavior)
                // But only if it's not actively processing a job
                if event.window().label() == "main" {
                    // Don't hide the window when it's processing a job
                    // This is handled by checking the activeJobId in the frontend
                    // We'll keep this commented for now
                    // event.window().hide().unwrap();
                }
            }
        })
        .setup(|app| {
            // Register global shortcut (Ctrl+K or Cmd+K)
            let app_handle = app.handle();
            let mut shortcut_manager = app_handle.global_shortcut_manager();
            
            // Register multiple shortcuts for better user experience
            let shortcuts = ["CommandOrControl+K", "CommandOrControl+Space"];
            for shortcut in shortcuts.iter() {
                let app_handle_clone = app_handle.clone();
                shortcut_manager
                    .register(shortcut, move || {
                        let window = app_handle_clone.get_window("main").unwrap();
                        toggle_spotlight_window(&window);
                    })
                    .unwrap_or_else(|e| println!("Failed to register shortcut {}: {}", shortcut, e));
            }
            
            // Start API server
            let app_state = app.state::<AppState>();
            match start_api_server(&app_state) {
                Ok(_) => println!("API server started"),
                Err(e) => eprintln!("Failed to start API server: {}", e),
            }
            
            // Get main window and set properties
            let main_window = app.get_window("main").unwrap();
            
            // Set window properties
            main_window.set_always_on_top(true).unwrap();
            
            // Position window at the top center (1/4 position)
            let monitor = main_window.current_monitor().unwrap().unwrap();
            let monitor_size = monitor.size();
            let window_size = main_window.inner_size().unwrap();
            
            let x = (monitor_size.width as i32 - window_size.width as i32) / 2;
            let y = monitor_size.height as i32 / 4 - window_size.height as i32 / 2;
            
            main_window.set_position(tauri::Position::Physical(tauri::PhysicalPosition { x, y })).unwrap();
            
            // Hide window on startup (will be shown with shortcut)
            main_window.hide().unwrap();
            
            println!("Using CSS backdrop-filter for visual effects across all platforms");
            
            // We'll handle cleanup in the quit_app command instead of using listen_global
            
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
} 