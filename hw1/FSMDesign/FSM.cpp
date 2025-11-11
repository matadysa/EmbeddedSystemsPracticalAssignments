#include <iostream>

using namespace std;

int main() {

    int n_states, n_transitions;
    cout  << "number of state and transitions: ";
    cin >> n_states >> n_transitions;

    int states[n_states];
    int transitions_head[n_transitions];
    int transitions_tail[n_transitions];


    for (size_t i = 0; i < n_states; i++)
    {
        states[i] = i;   
    }

    for (size_t i = 0; i < n_transitions; i++)
    {
        cout << "transition number " << i+1 << " : ";
        cin >> transitions_head[i] >> transitions_tail[i];
    }

    int current_state;
    cout << "starting state: ";
    cin >> current_state;


    while (true)
    {

        cout << "current state: " << current_state << "\n";

        int next_state;
        cout << "next state: ";  
        cin >> next_state;

        for (size_t i = 0; i < n_transitions; i++)
        {
            if (transitions_head[i] == current_state && transitions_tail[i] != next_state)
            {
                cout << "illegal transition, not defined in transitions table\n";
                break;
            }
            else if (transitions_head[i] == current_state && transitions_tail[i] == next_state)
            {
                cout << "transition successful\n";
                current_state = next_state;
                break;
            }
        }
    }   
    return 0;
}