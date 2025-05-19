class Instruction:
    def __init__(self, name, instr_str):
        self.name = name
        self.instr_str = instr_str
        self.stage_count = -1  # -1 = not fetched yet


class Pipeline:
    def __init__(self):
        #Step 0: Initialize all stages
        self.instructions = []
        self.stages = ["IF", "ID", "EX", "WB"]
        self.i_number = 1

    def add_instruction(self, instr_str):
        # Adding the instruction to the instruction queue (memory)
        i = Instruction(f"I{self.i_number}", instr_str)
        self.instructions.append(i)
        self.i_number += 1
        print(f"{i.name} ({instr_str}) added to instruction queue.")
        print("-" * 80)

    def step_pipeline(self):
        completed = []

        # Step 1: Advance existing instructions (not in fetch)
        for i in self.instructions:
            if i.stage_count >= 0 and i.stage_count < 3:
                i.stage_count += 1
            elif i.stage_count == 3:
                i.stage_count += 1
                completed.append(i)

        # Step 2: Try fetching a new instruction (if IF is free)
        if not any(i.stage_count == 0 for i in self.instructions):
            for i in self.instructions:
                if i.stage_count == -1:
                    i.stage_count = 0
                    print(f"{i.name} fetched into IF stage.")
                    break
        else:
            print("Structural Hazard: IF stage is already occupied. Fetch skipped.")

        # Step 3: Clean up completed instructions
        for i in completed:
            print(f"{i.name} has completed execution.")
            self.instructions.remove(i)

        print("-" * 80)

    def display_pipeline(self):
        # Step 4: Display pipeline diagram
        print("\n" + "PIPELINE DIAGRAM".center(80))
        print("-" * 80)
        stage_headers = ["Instruction".ljust(25)] + [stage.center(12) for stage in self.stages]
        print("".join(stage_headers))
        print("-" * 80)

        for i in self.instructions:
            row = f"{i.name} ({i.instr_str})".ljust(25)
            for s in range(4):
                if s == i.stage_count:
                    row += "**".center(12)
                else:
                    row += " ".center(12)
            print(row)

        if not self.instructions:
            print("Pipeline is empty. Please add instructions to get started.".center(80))
        print("-" * 80 + "\n")


def main():
    pipeline = Pipeline()
    while True:
        print("Pipelined Execution Menu:")
        print("1. Add Instruction")
        print("2. Step Pipeline")
        print("3. Display Pipeline")
        print("4. Exit")
        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            instr = input("Enter MIPS instruction (e.g., ADD $t0 $t1 $t2): ")
            pipeline.add_instruction(instr)
        elif choice == '2':
            pipeline.step_pipeline()
        elif choice == '3':
            pipeline.display_pipeline()
        elif choice == '4':
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please try again.")
        print()


main()
