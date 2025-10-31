#ifndef STEPPER_CONTROL_H
#define STEPPER_CONTROL_H
int16_t get_offset(int16_t potoffset)
{
    offset_queu.push(potoffset);
    while (offset_queu.size() > 50)
    {
        offset_queu.pop();
    }

    std::queue<int16_t> offset = offset_queu;
    while (offset.size() > 1)
    {
        offset.back() += offset.front();
        offset.pop();
    }
    offset.back() /= (int16_t)(offset_queu.size());
    return offset.back();
}

int16_t step_towards(int16_t tar, int16_t pos)
{
    // For timing see section 7.6 of drv8825 docs
    // https://www.ti.com/lit/ds/symlink/drv8825.pdf
    int16_t dir{0};
    if (tar > pos)
    {
        digitalWrite(DIR_PIN, LOW);
        delayMicroseconds(5); // Setup time
        dir = 1;
    }
    else if (tar < pos)
    {
        digitalWrite(DIR_PIN, HIGH);
        delayMicroseconds(5); // Setup time
        dir = -1;
    }

    if (not(tar == pos))
    {
        digitalWrite(STEP_PIN, HIGH);
        delayMicroseconds(5); // Pulse time
        // delay(150);            //!
        digitalWrite(STEP_PIN, LOW);
        delayMicroseconds(5); // Pulse time
        // delay(150);            //!
    }
    return dir;
}

bool step_stepper()
{
    int16_t potread = (int16_t)(map(analogRead(POT_PIN), (4096 / 2), (4096 / 1), -213, 213));
    int16_t stepper_offset = get_offset(potread);
    int16_t step_dir = step_towards(stepper_target, stepper_position - stepper_offset);
    stepper_position += step_dir;
    if (step_dir == 0)
    {
        return true;
    }
    else
    {
        return false;
    }
}

#endif // STEPPER_CONTROL_H