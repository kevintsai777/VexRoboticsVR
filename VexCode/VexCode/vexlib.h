#pragma once
// vexlib.h

#include <iostream>
#include <string>
#include "vex.h"

using namespace std;

enum waitUnits {
	seconds,
	milliseconds
};

void wait(int seconds, waitUnits unit_val = waitUnits::seconds);

struct ListNode {
    string instruction;
    int value;
    ListNode* next;

    // Default constructor
    ListNode() : instruction(), value(), next(nullptr) {}

    // Construct with values
    explicit ListNode(const string& ins, const int& val) : instruction(ins), value(val), next(nullptr) {}
};

extern ListNode* instruction_list;

// Insert a new node with `ins` and `val` at the end of `instruction_list`.
// Inline to allow definition in header.
inline void insert_instruction(const string& ins, int val) {
    ListNode* node = new ListNode(ins, val);
    if (!instruction_list) {
        instruction_list = node;
        return;
    }
    ListNode* cur = instruction_list;
    while (cur->next) cur = cur->next;
    cur->next = node;
}

int getInstructionList(void);
