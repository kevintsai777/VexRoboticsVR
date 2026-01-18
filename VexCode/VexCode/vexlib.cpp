// vexlib implementation

#include "vexlib.h"

#define WIN32_LEAN_AND_MEAN
#include <windows.h> // For Sleep function in Windows
#include <fstream>

void wait(int seconds, waitUnits unit_val) {
    // Correct conversion: if unit is seconds multiply by 1000, otherwise treat value as milliseconds
    int milliseconds = (unit_val == waitUnits::seconds) ? (seconds * 1000) : (seconds);
    //std::this_thread::sleep_for(std::chrono::seconds(seconds));
	cout << "Waiting for " << seconds << " seconds." << endl;
	Sleep(milliseconds); // Sleep function takes milliseconds
    insert_instruction("wait", seconds);
}

ListNode* instruction_list;

// TODO: Update this path as needed
#define InstructionFilepath "VexCode/instructions.txt"
int writeInstructionListToFile(const char* filepath);

int getInstructionList(void) {
    ListNode* node = instruction_list;
    int index = 0;

    if (node == nullptr) {
        cout << "Instruction list is empty." << endl;
        return 1;
    }
    insert_instruction("stop", 1);
    while (node != nullptr) {
        // Try to print a common `instruction` member; if that doesn't exist in your ListNode,
        // replace `node->instruction` with the correct member name or formatting.
        cout << "Instruction[" << index << "]: ";

        // Primary attempt (adjust if your ListNode differs)
        if (node->instruction == "stop") {
            cout << (node->value == 1? "stop" : "start") << '(' << node->value << ')' << endl;
        } else {
            cout << /* try printing member */ node->instruction << " " << node->value << endl;
		}

        node = node->next;
        ++index;
    }


    return writeInstructionListToFile(InstructionFilepath);
}

/* Implementation: writes the in-memory instruction list to a text file.
   Assumes ListNode has members: std::string instruction; int value; ListNode* next;
*/

int writeInstructionListToFile(const char* filepath) {
    if (instruction_list == nullptr) {
        cout << "Instruction list is empty. Nothing written to file." << endl;
        return 1;
    }

    std::ofstream ofs(filepath, std::ios::out | std::ios::trunc);
    if (!ofs.is_open()) {
        cout << "Failed to open file for writing: " << filepath << endl;
        return 2;
    }

    ListNode* node = instruction_list;
    int index = 0;
    while (node != nullptr) {
        // Format: index instruction value
        // If instruction contains spaces, consider quoting or using another delimiter.
        ofs << node->instruction << " " << node->value << '\n';
        node = node->next;
        ++index;
    }

    ofs.close();
    cout << "Wrote " << index << " instruction(s) to " << filepath << endl;
    return 0;
}