"""NCERT-based curriculum content for seeding the RAG vector store.

Each entry represents a chapter or topic with educational content.
Content is representative of NCERT textbooks for grades 6-10.
"""

CURRICULUM_ENTRIES = [
    # ─── Science ───────────────────────────────────────
    {
        "subject": "Science",
        "chapter": "Photosynthesis",
        "topic": "Photosynthesis",
        "grade": 8,
        "source": "ncert",
        "content": (
            "Photosynthesis is the process by which green plants prepare their own food. "
            "Plants use sunlight, water, and carbon dioxide to produce glucose and oxygen. "
            "The process occurs in the chloroplasts of plant cells, which contain chlorophyll. "
            "Chlorophyll is the green pigment that captures sunlight energy. "
            "The chemical equation for photosynthesis is: 6CO2 + 6H2O + sunlight -> C6H12O6 + 6O2. "
            "Carbon dioxide enters the plant through small pores called stomata on the leaves. "
            "Water is absorbed by the roots from the soil and transported to the leaves. "
            "Photosynthesis is essential for life on Earth as it produces oxygen and forms the base of food chains. "
            "Plants are called producers because they can make their own food through photosynthesis. "
            "The rate of photosynthesis is affected by factors like light intensity, carbon dioxide concentration, and temperature."
        ),
    },
    {
        "subject": "Science",
        "chapter": "Newton's Laws of Motion",
        "topic": "Newton's Laws of Motion",
        "grade": 9,
        "source": "ncert",
        "content": (
            "Newton's First Law of Motion states that an object at rest stays at rest, and an object in motion stays in motion with the same speed and in the same direction unless acted upon by an unbalanced external force. "
            "This law is also called the Law of Inertia. Inertia is the tendency of an object to resist changes in its state of motion. "
            "Newton's Second Law of Motion states that the rate of change of momentum of an object is directly proportional to the applied unbalanced force and takes place in the direction of the force. "
            "The mathematical expression is F = ma, where F is force, m is mass, and a is acceleration. "
            "Newton's Third Law of Motion states that for every action, there is an equal and opposite reaction. "
            "When you push a wall, the wall pushes you back with the same amount of force but in the opposite direction. "
            "These three laws form the foundation of classical mechanics and explain how objects move under the influence of forces."
        ),
    },
    {
        "subject": "Science",
        "chapter": "Chemical Reactions",
        "topic": "Chemical Reactions and Equations",
        "grade": 10,
        "source": "ncert",
        "content": (
            "A chemical reaction is a process in which one or more substances (reactants) are converted into one or more different substances (products). "
            "Chemical equations represent chemical reactions using chemical formulas and symbols. "
            "In a balanced chemical equation, the number of atoms of each element is equal on both sides of the equation. "
            "There are several types of chemical reactions: combination reactions, decomposition reactions, displacement reactions, double displacement reactions, and redox reactions. "
            "In a combination reaction, two or more substances combine to form a single product. "
            "In a decomposition reaction, a compound breaks down into simpler substances. "
            "A displacement reaction occurs when a more reactive element displaces a less reactive element from its compound. "
            "Oxidation is the gain of oxygen or loss of hydrogen, while reduction is the loss of oxygen or gain of hydrogen."
        ),
    },
    {
        "subject": "Science",
        "chapter": "Human Digestive System",
        "topic": "Nutrition in Humans",
        "grade": 7,
        "source": "ncert",
        "content": (
            "The human digestive system breaks down food into nutrients that the body can absorb and use. "
            "Digestion begins in the mouth, where teeth chew food and saliva starts breaking down carbohydrates. "
            "The food then travels through the oesophagus to the stomach. In the stomach, gastric juices containing hydrochloric acid and enzymes help digest proteins. "
            "The partially digested food moves to the small intestine, where most digestion and absorption occurs. "
            "The liver produces bile, which helps in the digestion of fats. The pancreas produces pancreatic juices containing enzymes. "
            "The inner wall of the small intestine has finger-like projections called villi that increase the surface area for absorption. "
            "The absorbed nutrients are transported through blood vessels to all parts of the body. "
            "The undigested food moves to the large intestine, where water is absorbed, and the remaining waste is expelled from the body."
        ),
    },

    # ─── Mathematics ───────────────────────────────────
    {
        "subject": "Mathematics",
        "chapter": "Algebraic Expressions",
        "topic": "Algebra",
        "grade": 8,
        "source": "ncert",
        "content": (
            "Algebraic expressions are mathematical phrases that contain variables, constants, and operations. "
            "A variable is a symbol (usually a letter like x, y, or z) that represents an unknown value. "
            "A constant is a fixed numerical value. Terms are the parts of an algebraic expression separated by + or - signs. "
            "Like terms have the same variable raised to the same power. Unlike terms have different variables or powers. "
            "To simplify algebraic expressions, combine like terms by adding or subtracting their coefficients. "
            "The distributive property states that a(b + c) = ab + ac. This is used to remove brackets. "
            "An equation is a statement that two expressions are equal, containing an equals sign. "
            "To solve an equation, find the value of the variable that makes the equation true by performing the same operation on both sides."
        ),
    },
    {
        "subject": "Mathematics",
        "chapter": "Geometry Basics",
        "topic": "Lines and Angles",
        "grade": 7,
        "source": "ncert",
        "content": (
            "Geometry is the branch of mathematics that deals with shapes, sizes, positions, and properties of space. "
            "A point is an exact position or location. A line is a straight path that extends infinitely in both directions. "
            "A line segment has two endpoints. A ray has one endpoint and extends infinitely in one direction. "
            "An angle is formed when two rays meet at a common endpoint called the vertex. "
            "Angles are measured in degrees. A right angle is exactly 90 degrees. An acute angle is less than 90 degrees. "
            "An obtuse angle is more than 90 degrees but less than 180 degrees. A straight angle is exactly 180 degrees. "
            "Complementary angles add up to 90 degrees. Supplementary angles add up to 180 degrees. "
            "When two lines intersect, vertically opposite angles are equal. When a transversal cuts parallel lines, corresponding angles are equal."
        ),
    },
    {
        "subject": "Mathematics",
        "chapter": "Quadratic Equations",
        "topic": "Quadratic Equations",
        "grade": 10,
        "source": "ncert",
        "content": (
            "A quadratic equation is an equation of the form ax^2 + bx + c = 0, where a, b, and c are real numbers and a is not equal to 0. "
            "The highest power of the variable is 2, which is why it is called a quadratic equation. "
            "There are several methods to solve quadratic equations: factorization, completing the square, and using the quadratic formula. "
            "The quadratic formula is x = [-b ± sqrt(b^2 - 4ac)] / 2a. "
            "The expression b^2 - 4ac is called the discriminant. It determines the nature of the roots. "
            "If the discriminant is positive, there are two distinct real roots. If it is zero, there is one real root (double root). "
            "If the discriminant is negative, there are no real roots (the roots are complex). "
            "Quadratic equations arise in many real-world situations, including physics problems involving projectile motion and optimization problems."
        ),
    },

    # ─── English ───────────────────────────────────────
    {
        "subject": "English",
        "chapter": "Tenses",
        "topic": "English Grammar",
        "grade": 8,
        "source": "ncert",
        "content": (
            "Tenses are verb forms that show the time of an action or state of being. There are three main tenses: past, present, and future. "
            "Each tense has four aspects: simple, continuous (progressive), perfect, and perfect continuous. "
            "The simple present tense is used for habits, general truths, and regular actions. Example: 'She reads every day.' "
            "The present continuous tense describes actions happening now. Example: 'She is reading right now.' "
            "The present perfect tense describes actions that started in the past and continue to the present or have relevance now. Example: 'She has read that book.' "
            "The simple past tense describes completed actions in the past. Example: 'She read yesterday.' "
            "The simple future tense describes actions that will happen. It uses 'will' or 'shall' with the base form of the verb. Example: 'She will read tomorrow.' "
            "Using the correct tense is essential for clear communication and accurate expression of time relationships."
        ),
    },
    {
        "subject": "English",
        "chapter": "Comprehension",
        "topic": "Reading Comprehension",
        "grade": 8,
        "source": "ncert",
        "content": (
            "Reading comprehension is the ability to understand, analyze, and interpret written text. "
            "To improve reading comprehension, first skim the text to get a general idea of what it is about. "
            "Then read carefully, paying attention to key ideas, supporting details, and the author's purpose. "
            "Make predictions about what will happen next or what the author will explain. "
            "Ask yourself questions as you read: Who is the main character? What is the main idea? Why did this happen? "
            "Summarize each paragraph in your own words to check your understanding. "
            "Look up unfamiliar words in a dictionary and note their meanings. "
            "Practice with different types of texts: stories, articles, poems, and informational passages. "
            "Regular reading habits improve vocabulary, grammar, and overall language skills."
        ),
    },

    # ─── Social Studies ─────────────────────────────────
    {
        "subject": "Social Studies",
        "chapter": "The Indian Constitution",
        "topic": "Civics",
        "grade": 8,
        "source": "ncert",
        "content": (
            "The Constitution of India was adopted on 26 November 1949 and came into effect on 26 January 1950. "
            "India celebrates 26 January as Republic Day every year. The Constitution is the supreme law of the land. "
            "Dr. B.R. Ambedkar is known as the chief architect of the Indian Constitution. "
            "The Preamble of the Constitution declares India to be a Sovereign, Socialist, Secular, Democratic Republic. "
            "Fundamental Rights are guaranteed to all citizens. These include the Right to Equality, Right to Freedom, Right against Exploitation, Right to Freedom of Religion, Cultural and Educational Rights, and Right to Constitutional Remedies. "
            "Directive Principles of State Policy guide the government in making laws and policies for the welfare of the people. "
            "Fundamental Duties were added by the 42nd Amendment in 1976. Citizens have duties such as respecting the national flag and protecting the environment. "
            "The Constitution provides for a federal system with a parliamentary form of government."
        ),
    },
    {
        "subject": "Social Studies",
        "chapter": "The French Revolution",
        "topic": "History",
        "grade": 9,
        "source": "ncert",
        "content": (
            "The French Revolution began in 1789 and transformed France from a monarchy to a republic. "
            "The revolution was caused by social inequality, economic problems, and the influence of Enlightenment ideas. "
            "French society was divided into three estates: the clergy (First Estate), nobility (Second Estate), and commoners (Third Estate). "
            "The Third Estate formed the National Assembly and took the Tennis Court Oath, promising not to separate until a constitution was established. "
            "On 14 July 1789, the people of Paris stormed the Bastille prison, a symbol of royal tyranny. "
            "The Declaration of the Rights of Man and of the Citizen was adopted, proclaiming liberty, equality, and fraternity. "
            "King Louis XVI was executed by guillotine in 1793. The Reign of Terror followed under Robespierre's leadership. "
            "Napoleon Bonaparte later rose to power and established himself as Emperor, spreading revolutionary ideas across Europe."
        ),
    },
    {
        "subject": "Social Studies",
        "chapter": "Geography of India",
        "topic": "Physical Features of India",
        "grade": 9,
        "source": "ncert",
        "content": (
            "India has diverse physical features including mountains, plateaus, plains, deserts, and coastal areas. "
            "The Himalayan mountains in the north are the youngest mountains in the world and stretch about 2500 kilometers. "
            "The Northern Indian Plains are formed by the alluvial deposits of the Indus, Ganga, and Brahmaputra rivers. "
            "This region is one of the most fertile agricultural areas in the world. "
            "The Peninsular Plateau is the oldest landmass in India, composed of igneous and metamorphic rocks. "
            "The Thar Desert in Rajasthan is the largest desert in India. "
            "India has a long coastline of about 7500 kilometers along the Arabian Sea and the Bay of Bengal. "
            "The Western Ghats and Eastern Ghats are mountain ranges along the western and eastern coasts respectively. "
            "India's diverse physical features influence its climate, agriculture, and the distribution of population and natural resources."
        ),
    },

    # ─── Hindi ──────────────────────────────────────────
    {
        "subject": "Hindi",
        "chapter": "हिंदी व्याकरण",
        "topic": "संज्ञा और सर्वनाम",
        "grade": 8,
        "source": "ncert",
        "content": (
            "संज्ञा किसी व्यक्ति, वस्तु, स्थान या भाव के नाम को कहते हैं। "
            "संज्ञा के पांच भेद हैं: व्यक्तिवाचक संज्ञा, जातिवाचक संज्ञा, समूहवाचक संज्ञा, द्रव्यवाचक संज्ञा, और भाववाचक संज्ञा। "
            "व्यक्तिवाचक संज्ञा किसी विशेष व्यक्ति या वस्तु के नाम को दर्शाती है, जैसे 'राम', 'गंगा'। "
            "जातिवाचक संज्ञा किसी जाति या वर्ग के सभी प्राणियों या वस्तुओं के लिए प्रयोग होती है, जैसे 'लड़का', 'नदी'। "
            "सर्वनाम वे शब्द हैं जो संज्ञा के स्थान पर प्रयोग किए जाते हैं। "
            "सर्वनाम के छह भेद हैं: पुरुषवाचक, निश्चयवाचक, अनिश्चयवाचक, संबंधवाचक, प्रश्नवाचक, और निजवाचक। "
            "पुरुषवाचक सर्वनाम तीन प्रकार के होते हैं: उत्तम पुरुष (मैं, हम), मध्यम पुरुष (तू, तुम, आप), और अन्य पुरुष (वह, वे, यह)। "
            "संज्ञा और सर्वनाम का सही प्रयोग वाक्य को स्पष्ट और प्रभावी बनाता है।"
        ),
    },
    {
        "subject": "Hindi",
        "chapter": "हिंदी साहित्य",
        "topic": "कहानी और निबंध",
        "grade": 9,
        "source": "ncert",
        "content": (
            "कहानी एक गद्य रचना है जिसमें जीवन की किसी घटना या अनुभव को रोचक ढंग से प्रस्तुत किया जाता है। "
            "कहानी के तत्व हैं: कथानक, पात्र, संवाद, वातावरण, और उद्देश्य। "
            "प्रेमचंद हिंदी साहित्य के सबसे प्रसिद्ध कहानीकार हैं। उनकी कहानियाँ गाँव के जीवन और सामाजिक मुद्दों पर आधारित हैं। "
            "निबंध एक गद्य रचना है जिसमें लेखक किसी विषय पर अपने विचार व्यक्त करता है। "
            "निबंध के मुख्य भाग हैं: भूमिका, विषय-विस्तार, और उपसंहार। "
            "अच्छा निबंध लिखने के लिए विषय पर गहन अध्ययन और स्पष्ट दृष्टिकोण आवश्यक है। "
            "हिंदी साहित्य में महादेवी वर्मा, हजारी प्रसाद द्विवेदी, और रामचंद्र शुक्ल जैसे महान निबंधकार हुए हैं।"
        ),
    },
]
