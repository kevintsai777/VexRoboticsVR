#include "vex.h"
using namespace vex;

void vexcodeInit(void) {
    insert_instruction("stop", 1);
    insert_instruction("degree", Drivetrain.getDegree());
    insert_instruction("direction", Drivetrain.getDirection());
    insert_instruction("velocity", Drivetrain.getVelocity());
    insert_instruction("stop", 0);
}

DrivetrainClass Drivetrain(0); // Global Drivetrain object

// Implementation of Drivetrain constructor
DrivetrainClass::DrivetrainClass(int init) : degree(init), dir(forward), vel(50) {}

char const stopModeNames[][6] = { "break", "coast", "hold" };

void DrivetrainClass::setRotation(int degree_value, unit unit_val) {
    // If required, convert radians -> degrees depending on unit_val
    cout << "rotate " << degree_value << (unit_val == degrees ? " degrees" : " radians") << endl;
    this->degree = degree_value;
    insert_instruction("degree", Drivetrain.getDegree());
}

void DrivetrainClass::drive(direction dir, velocity vel, velocityUnits unit_val) {
    cout << "driving " << (dir == forward ? "forward" : "reverse") << endl;
    this->dir = dir;
    this->vel = vel;
    insert_instruction("direction", Drivetrain.getDirection());
    insert_instruction("velocity", Drivetrain.getVelocity());
}

void DrivetrainClass::stop(stopMode mode) {
    cout << "Drivetrain stopped." << "(Mode:" << stopModeNames[mode] << ")" << endl;
    this->vel = 0;
    insert_instruction("velocity", Drivetrain.getVelocity());
}

void DrivetrainClass::turn(directionTurn turn, velocity vel, velocityUnits unit_val) {
    this->degree += (turn == vex_left ? -90 : 90); // Example adjustment
    //this->vel = vel;
    cout << "turning " << (turn == vex_left ? "left" : "right") << endl;
    cout << "Current rotation: " << this->degree << " degrees" << endl;
    insert_instruction("degree", Drivetrain.getDegree());
}

void DrivetrainClass::setDriveVelocity(velocity vel, velocityUnits unit_val) {
    this->vel = vel;
    cout << "Drive velocity set to " << vel << (unit_val == percent ? " percent" : (unit_val == rpm ? " rpm" : " dps")) << endl;
    insert_instruction("velocity", Drivetrain.getVelocity());
}

int DrivetrainClass::getDegree() { return this->degree; }
direction DrivetrainClass::getDirection() { return this->dir; }
velocity DrivetrainClass::getVelocity() { return this->vel; }

motor55::motor55(int init) : motorPort(init) {}

void motor55::spin(direction dir, velocity vel, velocityUnits unit_val) {
    cout << "Motor on port " << motorPort << " spinning " << (dir == forward ? "forward" : "reverse") << " at " << vel << (unit_val == percent ? " percent" : (unit_val == rpm ? " rpm" : " dps")) << endl;
}

void motor55::stop(stopMode mode) {
    cout << "Motor on port " << motorPort << " stopped. (Mode:" << stopModeNames[mode] << ")" << endl;
}