fn main() {
    let args = std::env::args().collect::<Vec<_>>();
    match taiko_cli::run_cli(&args) {
        Ok(output) => {
            println!("{output}");
        }
        Err(error) => {
            eprintln!("{error}");
            std::process::exit(2);
        }
    }
}
