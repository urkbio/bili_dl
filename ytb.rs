use std::process::Command;
use std::io::Write;
use std::io::stdout;

fn main() {
    let mut url = String::new();
    print!("Enter the YouTube video URL: ");
    stdout().flush().unwrap();
    std::io::stdin().read_line(&mut url).unwrap();

    let output = Command::new("youtube-dl")
        .arg("-f")
        .arg("best")
        .arg("-o")
        .arg("%(title)s.%(ext)s")
        .arg(&url)
        .output()
        .expect("Failed to download the video");

    if output.status.success() {
        println!("Video downloaded successfully");
    } else {
        println!("Failed to download the video");
    }
}
