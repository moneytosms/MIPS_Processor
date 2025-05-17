class Instruction:
    def __init__(self, name):
        self.name = name
        self.stage_count = 0

class Pipeline:
    def __init__(self):
        self.instructions = []
        self.stages = ["IF", "ID", "EX", "WB"]
        self.i_number = 1

    def add_instruction(self):
        if any(i.stage_count == 0 for i in self.instructions):
            print("Structural Hazard: Cannot add instruction. IF stage is under use.")
        else:
            i = Instruction(f"Instruction{self.i_number}")
            self.instructions.append(i)
            self.i_number += 1
            print(f"{i.name} added to pipeline.")

    def step_pipeline(self):
        completed = []
        for i in self.instructions:
            if i.stage_count < 4:
                i.stage_count += 1
            if i.stage_count == 4:
                completed.append(i)

        for i in completed:
            print(f"{i.name} has completed execution.")
            self.instructions.remove(i)

    def display_pipeline(self):
        print("\nPipeline Diagram: ".center(40))
        print()
        print("              " + "  ".join(self.stages))
        
        for i in self.instructions:
            row = f"{i.name:<14}"
            for s in range(4):
                if s == i.stage_count:
                    row += "**  " 
                else:
                    row += "    "
            print(row)
        
        if not self.instructions:
            print("Pipeline is empty. Please add instructions to get started.")
        print()

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
            pipeline.add_instruction()
        elif choice == '2':
            pipeline.step_pipeline()
        elif choice == '3':
            pipeline.display_pipeline()
        elif choice == '4':
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please try again.")

main()
