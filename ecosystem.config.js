module.exports = {
  apps : [{
    name   : "NovelNotlify", // A user-friendly name for your application
    script : "./venv/bin/python", // UPDATE WITH ABSOLUTE PATH
    args   : "start_bot.py", // The Python script to execute
    interpreter : "none", // PM2 should not try to interpret the script itself
    watch  : true, // Restart the app if file changes are detected
    ignore_watch : ["node_modules", ".git", "*.log", "venv", ".venv", "novels.db", "novels.db-journal"], // Files/folders to ignore when watching
    exp_backoff_restart_delay: 100 // Delay between restarts in milliseconds
  }]
};