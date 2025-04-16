class Solution {
public:
    bool isPalindrome(long long x) {
        if(x<0){
            return false;
        }
        long long original = x;
        long long reversed = 0;

        while(x!=0){
                int digit= x%10;
                reversed = reversed*10+digit;
                x/=10; 
        }
        if(original==reversed){
            return true;
        }
    return 0;
    }
};