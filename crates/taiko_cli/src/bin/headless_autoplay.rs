fn main() {
    let raw_args = std::env::args().collect::<Vec<_>>();
    let mut args = vec![raw_args.first().cloned().unwrap_or_else(|| "headless_autoplay".to_string())];
    args.push("headless".to_string());
    args.push("autoplay".to_string());
    args.extend(raw_args.into_iter().skip(1));
    match taiko_cli::run_cli(&args) {
        Ok(output) => println!("{output}"),
        Err(error) => {
            eprintln!("{error}");
            std::process::exit(2);
        }
    }
}
