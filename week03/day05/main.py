import argparse

# --- station 1: validation ---
def validate_data(input_file, output_folder):
    print(f"✅ Validating {input_file} → saving report in {output_folder}")

# --- station 2: transformation ---
def transform_data(input_file, output_folder):
    print(f"🍳 Transforming {input_file} → output to {output_folder}")

# --- station 3: reporting ---
def report_data(input_file, output_folder):
    print(f"📊 Generating report from {input_file} → {output_folder}")

# --- waiter logic ---
def main():
    parser = argparse.ArgumentParser(prog="dataproc", description="Data pipeline CLI")
    subparsers = parser.add_subparsers(dest="command")

    # validate
    val = subparsers.add_parser("validate", help="Check data quality")
    val.add_argument("--in", dest="input", required=True)
    val.add_argument("--out", dest="output", required=True)

    # transform
    trans = subparsers.add_parser("transform", help="Transform data")
    trans.add_argument("--in", dest="input", required=True)
    trans.add_argument("--out", dest="output", required=True)

    # report
    rep = subparsers.add_parser("report", help="Generate report")
    rep.add_argument("--in", dest="input", required=True)
    rep.add_argument("--out", dest="output", required=True)

    # read the user's order
    args = parser.parse_args()

    # route to correct function
    if args.command == "validate":
        validate_data(args.input, args.output)
    elif args.command == "transform":
        transform_data(args.input, args.output)
    elif args.command == "report":
        report_data(args.input, args.output)
    elif args.command == "hello":
        print(f"👋 Hello, {args.name}!")    
    else:
        parser.print_help()
        
        

if __name__ == "__main__":
    main()
