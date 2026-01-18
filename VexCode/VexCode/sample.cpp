// sample.cpp : This file contains the 'main' function. Program execution begins and ends there.
//
// Include the V5 mock library
#include "vex.h"

// Allows for easier use of the VEX Library
using namespace vex;

// main function - entry point of the program
int main() {

    vexcodeInit();

    // Set drivetrain rotation (reset heading to 90 degrees)
    Drivetrain.setRotation(90, degrees);

    // Drive forward at default velocity
    Drivetrain.drive(forward);
    wait(2, seconds);

    // Drive reverse at 25% velocity
    Drivetrain.drive(reverse, 25, velocityUnits::pct);
    wait(2, seconds);
    Drivetrain.stop(vex_break);

    // Turn right, then left, then stop
    Drivetrain.turn(vex_right);
    wait(2, seconds);
    Drivetrain.turn(vex_left);
    wait(2, seconds);
    Drivetrain.stop(vex_break);

    // Drive forward, then coast to a stop
    Drivetrain.setDriveVelocity(100, velocityUnits::pct);
    Drivetrain.drive(forward);
    wait(2, seconds);
    Drivetrain.stop(vex_coast);

    return getInstructionList();
}